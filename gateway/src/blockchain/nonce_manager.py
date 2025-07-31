import asyncio
import logging
from typing import Optional, Set
from web3 import Web3
from web3.exceptions import TransactionNotFound

logger = logging.getLogger(__name__)

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
                self.current_nonce = await self.web3.eth.get_transaction_count(self.account_address)
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
                receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
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
            self.current_nonce = await self.web3.eth.get_transaction_count(self.account_address)
            self.pending_transactions.clear()
            logger.info(f"Nonce resetado para: {self.current_nonce}")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do gerenciador para debug"""
        return {
            "current_nonce": self.current_nonce,
            "pending_transactions": len(self.pending_transactions),
            "account_address": self.account_address
        }
    
    async def send_transaction_with_retry(self, transaction_builder, max_retries: int = 3) -> dict:
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
                tx = transaction_builder.build_transaction({
                    'from': self.account_address,
                    'nonce': nonce,
                    'gasPrice': await self.web3.eth.gas_price,
                    'chainId': await self.web3.eth.chain_id
                })
                
                # 3. Assinar e enviar transação
                signed_tx = self.web3.eth.account.sign_transaction(tx, self.web3.eth.account.from_key(tx['privateKey']))
                tx_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
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