from web3 import Web3
from web3.exceptions import ContractLogicError
from config.settings import settings
from .nonce_manager import NoncePool
import json
import os
import logging
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self, private_key=None):
        # Configurar pool de conexões para melhor performance
        self.web3 = Web3(Web3.HTTPProvider(
            settings.RPC_URL,
            request_kwargs={
                'timeout': 30,
                'headers': {'Content-Type': 'application/json'}
            }
        ))
        
        # Verificar conexão com Besu
        if not self.web3.is_connected():
            raise ConnectionError(f"Não foi possível conectar ao Besu em {settings.RPC_URL}")
        
        # Configurar conta
        key = private_key or settings.OWNER_PRIVATE_KEY
        self.account = self.web3.eth.account.from_key(key)
        self.web3.eth.default_account = self.account.address
        
        # Inicializar NoncePool (substitui NonceManager)
        self.nonce_pool = NoncePool(self.web3, pool_size=100)  # Pool maior para alta concorrência
        
        # Carregar ABI
        abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'SASSharedRegistry.json')
        try:
            with open(abi_path) as f:
                abi_data = json.load(f)
                # Extrair apenas o array ABI do arquivo do Hardhat
                if isinstance(abi_data, dict) and 'abi' in abi_data:
                    abi = abi_data['abi']
                else:
                    abi = abi_data
        except FileNotFoundError:
            raise FileNotFoundError(f"ABI não encontrado em {abi_path}")
        
        # Instanciar contrato
        self.contract = self.web3.eth.contract(
            address=settings.CONTRACT_ADDRESS, 
            abi=abi
        )
        
        # Cache para resultados
        self._cache = {}
        
        logger.info(f"Conectado ao Besu. Conta: {self.account.address}")
        logger.info(f"Contrato: {settings.CONTRACT_ADDRESS}")
        logger.info(f"NoncePool inicializado para conta: {self.account.address}")
        logger.info(f"Configurações de performance: Gas={settings.GAS_PRICE}, Batch={settings.BATCH_SIZE}")

    def get_event_filter(self, event_name, from_block='latest'):
        """Cria filtro para eventos do contrato"""
        try:
            event_abi = getattr(self.contract.events, event_name)._get_event_abi()
            # Usar w3.eth.filter para eventos futuros
            event_signature_hash = self.web3.keccak(text=f"{event_name}({','.join([input['type'] for input in event_abi['inputs']])})").hex()
            filter_params = {
                'address': self.contract.address,
                'topics': [event_signature_hash],
                'fromBlock': from_block
            }
            return self.web3.eth.filter(filter_params)
        except AttributeError:
            logger.error(f"Evento {event_name} não encontrado no contrato")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar filtro para evento {event_name}: {e}")
            raise

    def get_latest_block(self):
        """Retorna o número do último bloco"""
        return self.web3.eth.block_number

    def get_gas_price(self):
        """Obtém o preço do gas otimizado"""
        # Usar gas price fixo para melhor performance
        return settings.GAS_PRICE

    def estimate_gas(self, function_call):
        """Estima o gas necessário para uma transação"""
        try:
            estimated_gas = function_call.estimate_gas()
            # Adicionar margem de segurança
            return min(estimated_gas + 50000, settings.GAS_LIMIT)
        except ContractLogicError as e:
            logger.error(f"Erro ao estimar gas: {e}")
            raise

    def get_nonce(self):
        """Obtém o nonce atual da conta"""
        return self.web3.eth.get_transaction_count(self.account.address)

    def build_transaction(self, function_call, gas_limit=None):
        """Constrói uma transação otimizada para Besu"""
        gas_price = self.get_gas_price()
        nonce = self.get_nonce()
        
        # Usar gas limit otimizado
        if gas_limit is None:
            gas_limit = min(self.estimate_gas(function_call), settings.GAS_LIMIT)
        
        tx_params = {
            'from': self.account.address,
            'gasPrice': gas_price,
            'gas': gas_limit,
            'nonce': nonce,
            'chainId': settings.CHAIN_ID
        }
        
        # Adicionar maxPriorityFeePerGas se suportado
        if hasattr(settings, 'MAX_PRIORITY_FEE'):
            tx_params['maxPriorityFeePerGas'] = settings.MAX_PRIORITY_FEE
        
        return function_call.build_transaction(tx_params)

    async def send_transaction_with_nonce_manager(self, function_call, gas_limit=None):
        """Envia transação usando NoncePool com retry"""
        try:
            # Usar NoncePool para enviar transação com retry
            receipt = await self.send_transaction_with_pool_and_retry(function_call, gas_limit)
            logger.info(f"Transação enviada com NoncePool: {receipt['transactionHash'].hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Erro ao enviar transação com NoncePool: {e}")
            raise

    def send_transaction(self, function_call, gas_limit=None):
        """Envia transação de forma síncrona"""
        try:
            # Construir transação
            tx = self.build_transaction(function_call, gas_limit)
            
            # Assinar e enviar transação
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key.hex())
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Aguardar confirmação
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            logger.info(f"Transação enviada: {receipt['transactionHash'].hex()}")
            return receipt
        except Exception as e:
            logger.error(f"Erro ao enviar transação: {e}")
            raise

    def call_function(self, function_call):
        """Executa função de leitura (call)"""
        try:
            return function_call.call()
        except Exception as e:
            logger.error(f"Erro ao executar função: {e}")
            raise

    # Funções SAS-SAS com NonceManager (recomendadas para redes reais)
    async def registration_with_nonce_manager(self, data: dict):
        """Executa operação SAS-SAS Registration usando NonceManager"""
        try:
            args = [
                data["fccId"],
                data["userId"],
                data["cbsdSerialNumber"],
                data["callSign"],
                data["cbsdCategory"],
                data["airInterface"],
                data["measCapability"],
                data["eirpCapability"],
                data["latitude"],
                data["longitude"],
                data["height"],
                data["heightType"],
                data["indoorDeployment"],
                data["antennaGain"],
                data["antennaBeamwidth"],
                data["antennaAzimuth"],
                data["groupingParam"],
                data["cbsdAddress"]
            ]
            tx = self.contract.functions.registration(args)
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro na operação registration com NonceManager: {e}")
            raise

    # Funções SAS-SAS (métodos legados - mantidos para compatibilidade)
    def registration(self, data: dict):
        """Executa operação SAS-SAS Registration (struct RegistrationRequest)"""
        try:
            args = [
                data["fccId"],
                data["userId"],
                data["cbsdSerialNumber"],
                data["callSign"],
                data["cbsdCategory"],
                data["airInterface"],
                data["measCapability"],
                data["eirpCapability"],
                data["latitude"],
                data["longitude"],
                data["height"],
                data["heightType"],
                data["indoorDeployment"],
                data["antennaGain"],
                data["antennaBeamwidth"],
                data["antennaAzimuth"],
                data["groupingParam"],
                data["cbsdAddress"]
            ]
            tx = self.contract.functions.registration(args)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação registration: {e}")
            raise

    async def grant_with_nonce_manager(self, data: dict):
        """Executa operação SAS-SAS Grant usando NonceManager"""
        try:
            args = [
                data["fccId"],
                data["cbsdSerialNumber"],
                data["channelType"],
                data["maxEirp"],
                data["lowFrequency"],
                data["highFrequency"],
                data["requestedMaxEirp"],
                data["requestedLowFrequency"],
                data["requestedHighFrequency"],
                data["grantExpireTime"]
            ]
            tx = self.contract.functions.grant(args)
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro na operação grant com NonceManager: {e}")
            raise

    def grant(self, data: dict):
        """Executa operação SAS-SAS Grant (struct GrantRequest)"""
        try:
            args = [
                data["fccId"],
                data["cbsdSerialNumber"],
                data["channelType"],
                data["maxEirp"],
                data["lowFrequency"],
                data["highFrequency"],
                data["requestedMaxEirp"],
                data["requestedLowFrequency"],
                data["requestedHighFrequency"],
                data["grantExpireTime"]
            ]
            tx = self.contract.functions.grant(args)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação grant: {e}")
            raise

    async def relinquishment_with_nonce_manager(self, data: dict):
        """Executa operação SAS-SAS Relinquishment usando NonceManager"""
        try:
            tx = self.contract.functions.relinquishment(
                data["fccId"], data["cbsdSerialNumber"], data["grantId"]
            )
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro na operação relinquishment com NonceManager: {e}")
            raise

    async def deregistration_with_nonce_manager(self, data: dict):
        """Executa operação SAS-SAS Deregistration usando NonceManager"""
        try:
            tx = self.contract.functions.deregistration(
                data["fccId"], data["cbsdSerialNumber"]
            )
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro na operação deregistration com NonceManager: {e}")
            raise

    def relinquishment(self, data: dict):
        """Executa operação SAS-SAS Relinquishment"""
        try:
            tx = self.contract.functions.relinquishment(
                data["fccId"], data["cbsdSerialNumber"], data["grantId"]
            )
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação relinquishment: {e}")
            raise

    def deregistration(self, data: dict):
        """Executa operação SAS-SAS Deregistration"""
        try:
            tx = self.contract.functions.deregistration(
                data["fccId"], data["cbsdSerialNumber"]
            )
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação deregistration: {e}")
            raise

    # Funções de autorização SAS com NonceManager
    async def authorize_sas_with_nonce_manager(self, sas_address: str):
        """Autoriza um endereço como SAS usando NonceManager"""
        try:
            # Converter endereço para o tipo correto
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.authorizeSAS(address)
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro ao autorizar SAS {sas_address} com NonceManager: {e}")
            raise

    async def revoke_sas_with_nonce_manager(self, sas_address: str):
        """Revoga autorização de um SAS usando NonceManager"""
        try:
            # Converter endereço para o tipo correto
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.revokeSAS(address)
            return await self.send_transaction_with_nonce_manager(tx)
        except Exception as e:
            logger.error(f"Erro ao revogar SAS {sas_address} com NonceManager: {e}")
            raise

    # Funções de autorização SAS (métodos legados - mantidos para compatibilidade)
    def authorize_sas(self, sas_address: str):
        """Autoriza um endereço como SAS"""
        try:
            # Converter endereço para o tipo correto
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.authorizeSAS(address)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro ao autorizar SAS {sas_address}: {e}")
            raise

    def revoke_sas(self, sas_address: str):
        """Revoga autorização de um SAS"""
        try:
            # Converter endereço para o tipo correto
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.revokeSAS(address)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro ao revogar SAS {sas_address}: {e}")
            raise

    def is_authorized_sas(self, sas_address: str):
        """Verifica se um endereço é um SAS autorizado"""
        try:
            # Converter endereço para o tipo correto
            address = self.web3.to_checksum_address(sas_address)
            return self.contract.functions.authorizedSAS(address).call()
        except Exception as e:
            logger.error(f"Erro ao verificar SAS {sas_address}: {e}")
            raise

    def get_owner(self):
        """Obtém o endereço do owner do contrato"""
        try:
            return self.contract.functions.owner().call()
        except Exception as e:
            logger.error(f"Erro ao obter owner: {e}")
            raise

    async def send_transaction_with_pool_and_retry(self, function_call, gas_limit=None, max_retries=3):
        """
        Envia transação usando NoncePool com retry automático
        
        Este método resolve o problema de "Nonce too low" usando:
        1. NoncePool para obter nonces pré-alocados
        2. Retry automático em caso de conflito
        3. Exponential backoff para evitar spam
        """
        for attempt in range(max_retries):
            try:
                # 1. Obter nonce do pool
                nonce = await self.nonce_pool.get_nonce(self.account.address)
                
                # 2. Construir transação
                gas_price = self.get_gas_price()
                chain_id = self.web3.eth.chain_id
                tx = function_call.build_transaction({
                    'from': self.account.address,
                    'nonce': nonce,
                    'gasPrice': gas_price,
                    'chainId': chain_id
                })
                
                # 3. Assinar e enviar transação
                signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key.hex())
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                
                logger.info(f"Transação enviada com NoncePool (async): {tx_hash.hex()}")
                return {
                    'success': True,
                    'transaction_hash': tx_hash.hex(),
                    'status': 'submitted',
                    'nonce': nonce
                }
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Detectar erros de nonce
                if "nonce" in error_msg or "replacement" in error_msg or "already known" in error_msg:
                    logger.warning(f"Erro de nonce na tentativa {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        await self.nonce_pool.handle_nonce_conflict(self.account.address)
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                
                # Outros erros: re-raise
                raise e
        
        raise Exception(f"Falha ao enviar transação após {max_retries} tentativas")

    async def send_transaction_async(self, function_call, gas_limit=None):
        """Envia transação de forma assíncrona usando NoncePool"""
        try:
            # Usar NoncePool para enviar transação sem aguardar confirmação
            nonce = await self.nonce_pool.get_nonce(self.account.address)
            
            # Construir transação
            gas_price = self.get_gas_price()
            chain_id = self.web3.eth.chain_id
            tx = function_call.build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gasPrice': gas_price,
                'chainId': chain_id
            })
            
            # Assinar e enviar transação
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key.hex())
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            logger.info(f"Transação enviada com NoncePool (async): {tx_hash.hex()}")
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'status': 'submitted',
                'nonce': nonce
            }
            
        except Exception as e:
            logger.error(f"Erro ao enviar transação (async): {e}")
            raise

    async def send_transaction_with_nonce_manager_async(self, function_call, gas_limit=None):
        """Envia transação assíncrona usando NoncePool com retry"""
        try:
            return await self.send_transaction_with_pool_and_retry(function_call, gas_limit)
        except Exception as e:
            logger.error(f"Erro ao enviar transação com NoncePool (async): {e}")
            raise

    # Funções SAS-SAS assíncronas (SEM aguardar confirmação)
    async def registration_async(self, data: dict):
        """Executa operação SAS-SAS Registration de forma assíncrona"""
        try:
            args = [
                data["fccId"],
                data["userId"],
                data["cbsdSerialNumber"],
                data["callSign"],
                data["cbsdCategory"],
                data["airInterface"],
                data["measCapability"],
                data["eirpCapability"],
                data["latitude"],
                data["longitude"],
                data["height"],
                data["heightType"],
                data["indoorDeployment"],
                data["antennaGain"],
                data["antennaBeamwidth"],
                data["antennaAzimuth"],
                data["groupingParam"],
                data["cbsdAddress"]
            ]
            tx = self.contract.functions.registration(args)
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro na operação registration (async): {e}")
            raise

    async def grant_async(self, data: dict):
        """Executa operação SAS-SAS Grant de forma assíncrona"""
        try:
            # Criar struct GrantRequest
            grant_request = [
                data["fccId"],
                data["cbsdSerialNumber"],
                data["channelType"],
                data["maxEirp"],
                data["lowFrequency"],
                data["highFrequency"],
                data["requestedMaxEirp"],
                data["requestedLowFrequency"],
                data["requestedHighFrequency"],
                data["grantExpireTime"]
            ]
            tx = self.contract.functions.grant(grant_request)
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro na operação grant (async): {e}")
            raise

    async def relinquishment_async(self, data: dict):
        """Executa operação SAS-SAS Relinquishment de forma assíncrona"""
        try:
            tx = self.contract.functions.relinquishment(
                data["fccId"], data["cbsdSerialNumber"], data["grantId"]
            )
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro na operação relinquishment (async): {e}")
            raise

    async def deregistration_async(self, data: dict):
        """Executa operação SAS-SAS Deregistration de forma assíncrona"""
        try:
            tx = self.contract.functions.deregistration(
                data["fccId"], data["cbsdSerialNumber"]
            )
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro na operação deregistration (async): {e}")
            raise

    async def authorize_sas_async(self, sas_address: str):
        """Autoriza um SAS de forma assíncrona"""
        try:
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.authorizeSAS(address)
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro ao autorizar SAS (async) {sas_address}: {e}")
            raise

    async def revoke_sas_async(self, sas_address: str):
        """Revoga um SAS de forma assíncrona"""
        try:
            address = self.web3.to_checksum_address(sas_address)
            tx = self.contract.functions.revokeSAS(address)
            return await self.send_transaction_with_nonce_manager_async(tx)
        except Exception as e:
            logger.error(f"Erro ao revogar SAS (async) {sas_address}: {e}")
            raise 

    def get_nonce_manager_stats(self):
        """Obtém estatísticas do NoncePool para debug"""
        try:
            return self.nonce_pool.get_stats()
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do NoncePool: {e}")
            return {} 

    @lru_cache(maxsize=100)
    def is_authorized_sas_cached(self, sas_address: str):
        """Versão cacheada da verificação de autorização"""
        try:
            return self.contract.functions.isAuthorizedSAS(sas_address).call()
        except Exception as e:
            logger.error(f"Erro ao verificar autorização de SAS {sas_address}: {e}")
            return False 