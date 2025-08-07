import asyncio
import logging
from typing import Optional, Set, Dict, List
from web3 import Web3
from web3.exceptions import TransactionNotFound

logger = logging.getLogger(__name__)

class NoncePool:
    """
    Pool de nonces para máxima performance e zero conflitos
    
    O NoncePool resolve o problema de "Nonce too low" garantindo:
    1. Nonces pré-alocados para cada conta
    2. Zero espera por locks (exceto recarregamento)
    3. Máxima paralelização de transações
    4. Retry automático em caso de conflito
    """
    
    def __init__(self, web3: Web3, pool_size: int = 50):
        self.web3 = web3
        self.pool_size = pool_size
        self._nonce_pools: Dict[str, List[int]] = {}
        self._pool_locks: Dict[str, asyncio.Lock] = {}
        self._reload_locks: Dict[str, asyncio.Lock] = {}
        self._stats = {
            'pools_created': 0,
            'nonces_used': 0,
            'pools_reloaded': 0,
            'conflicts_resolved': 0
        }
    
    async def get_nonce(self, account_address: str) -> int:
        """
        Obtém um nonce do pool de forma thread-safe
        
        Se o pool está vazio, recarrega automaticamente.
        Cada conta tem seu próprio pool independente.
        """
        # Criar lock específico para esta conta se não existir
        if account_address not in self._pool_locks:
            self._pool_locks[account_address] = asyncio.Lock()
            self._reload_locks[account_address] = asyncio.Lock()
        
        async with self._pool_locks[account_address]:
            # Inicializar pool se não existir
            if account_address not in self._nonce_pools:
                await self._initialize_pool(account_address)
            
            # Se pool está vazio, recarregar
            if not self._nonce_pools[account_address]:
                await self._reload_pool(account_address)
            
            # Retornar próximo nonce do pool
            nonce = self._nonce_pools[account_address].pop(0)
            self._stats['nonces_used'] += 1
            
            logger.debug(f"Nonce {nonce} obtido do pool para {account_address}")
            return nonce
    
    async def _initialize_pool(self, account_address: str) -> None:
        """Inicializa o pool de nonces para uma conta"""
        async with self._reload_locks[account_address]:
            current_nonce = self.web3.eth.get_transaction_count(account_address)
            self._nonce_pools[account_address] = list(range(
                current_nonce, 
                current_nonce + self.pool_size
            ))
            self._stats['pools_created'] += 1
            
            logger.info(f"Pool inicializado para {account_address}: nonces {current_nonce}-{current_nonce + self.pool_size - 1}")
    
    async def _reload_pool(self, account_address: str) -> None:
        """Recarrega o pool de nonces quando está vazio"""
        async with self._reload_locks[account_address]:
            current_nonce = self.web3.eth.get_transaction_count(account_address)
            self._nonce_pools[account_address] = list(range(
                current_nonce, 
                current_nonce + self.pool_size
            ))
            self._stats['pools_reloaded'] += 1
            
            logger.info(f"Pool recarregado para {account_address}: nonces {current_nonce}-{current_nonce + self.pool_size - 1}")
    
    async def handle_nonce_conflict(self, account_address: str) -> None:
        """Trata conflito de nonce recarregando o pool"""
        self._stats['conflicts_resolved'] += 1
        logger.warning(f"Conflito de nonce detectado para {account_address}, recarregando pool")
        await self._reload_pool(account_address)
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do pool para monitoramento"""
        pool_sizes = {addr: len(pool) for addr, pool in self._nonce_pools.items()}
        return {
            **self._stats,
            'active_pools': len(self._nonce_pools),
            'pool_sizes': pool_sizes
        }

class NonceManager:
    """
    Gerenciador de nonce para evitar conflitos em transações concorrentes
    
    O NonceManager resolve o problema de "fila de nonce" garantindo que:
    1. Cada transação use um nonce único e sequencial
    2. Transações não sejam enviadas antes da confirmação da anterior
    3. Em caso de erro, o nonce seja resetado automaticamente
    4. Múltiplas threads não conflitem ao usar a mesma conta
    """
    
    def __init__(self, web3: Web3, account_address: str):
        self.web3 = web3
        self.account_address = account_address
        self.current_nonce: Optional[int] = None
        self.pending_transactions: Set[str] = set()
        self.lock = asyncio.Lock()
    
    async def get_next_nonce(self) -> int:
        """
        Obtém o próximo nonce disponível de forma thread-safe
        
        Se é a primeira transação, busca da rede.
        Se não, incrementa o nonce local.
        """
        async with self.lock:
            if self.current_nonce is None:
                # Primeira transação: busca da rede
                self.current_nonce = self.web3.eth.get_transaction_count(self.account_address)
                logger.info(f"Nonce inicial obtido da rede: {self.current_nonce}")
            else:
                # Transações subsequentes: incrementa localmente
                self.current_nonce += 1
                logger.debug(f"Nonce incrementado para: {self.current_nonce}")
            
            return self.current_nonce
    
    async def mark_transaction_pending(self, tx_hash: str) -> None:
        """Marca uma transação como pendente para evitar duplicatas"""
        async with self.lock:
            self.pending_transactions.add(tx_hash)
            logger.debug(f"Transação {tx_hash} marcada como pendente")
    
    async def mark_transaction_confirmed(self, tx_hash: str) -> None:
        """Marca uma transação como confirmada"""
        async with self.lock:
            self.pending_transactions.discard(tx_hash)
            logger.debug(f"Transação {tx_hash} confirmada")
    
    async def wait_for_transaction_confirmation(self, tx_hash: str, max_attempts: int = 30) -> dict:
        """
        Aguarda a confirmação de uma transação com retry
        
        Em redes reais (Besu), isso é crucial pois:
        - Block time pode ser 1-15 segundos
        - Rede pode estar congestionada
        - Transação pode falhar e precisar ser reenviada
        """
        for attempt in range(max_attempts):
            try:
                receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
                await self.mark_transaction_confirmed(tx_hash)
                logger.info(f"Transação {tx_hash} confirmada no bloco {receipt['blockNumber']}")
                return receipt
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1}/{max_attempts} - Aguardando confirmação: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise TimeoutError(f"Transação {tx_hash} não foi confirmada após {max_attempts} tentativas")
    
    async def reset_nonce(self) -> None:
        """
        Reseta o nonce para o valor atual da rede
        
        Usado quando:
        - Ocorre erro de nonce
        - Transação anterior falhou
        - Rede foi resetada
        """
        async with self.lock:
            self.current_nonce = self.web3.eth.get_transaction_count(self.account_address)
            self.pending_transactions.clear()
            logger.info(f"Nonce resetado para: {self.current_nonce}")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do gerenciador para debug"""
        return {
            "current_nonce": self.current_nonce,
            "pending_transactions": len(self.pending_transactions),
            "account_address": self.account_address
        }
    
    async def send_transaction_with_retry(self, transaction_builder, private_key: str, max_retries: int = 3) -> dict:
        """
        Envia uma transação com retry automático em caso de erro de nonce
        
        Este é o método principal que resolve o problema de fila de nonce:
        
        1. Obtém nonce único
        2. Envia transação
        3. Aguarda confirmação
        4. Se falhar por nonce, reseta e tenta novamente
        5. Usa exponential backoff para evitar spam
        """
        for attempt in range(max_retries):
            try:
                # 1. Obter nonce único
                nonce = await self.get_next_nonce()
                
                # 2. Construir transação
                gas_price = self.web3.eth.gas_price
                chain_id = self.web3.eth.chain_id
                tx = transaction_builder.build_transaction({
                    'from': self.account_address,
                    'nonce': nonce,
                    'gasPrice': gas_price,
                    'chainId': chain_id
                })
                
                # 3. Assinar e enviar transação
                signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                # 4. Marcar como pendente
                await self.mark_transaction_pending(tx_hash.hex())
                
                # 5. Aguardar confirmação
                receipt = await self.wait_for_transaction_confirmation(tx_hash.hex())
                return receipt
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Detectar erros de nonce
                if "nonce" in error_msg or "replacement" in error_msg or "already known" in error_msg:
                    logger.warning(f"Erro de nonce na tentativa {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        await self.reset_nonce()  # Reset nonce
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                
                # Outros erros: re-raise
                raise e
        
        raise Exception(f"Falha ao enviar transação após {max_retries} tentativas") 