from web3 import Web3
from web3.exceptions import ContractLogicError
from src.config.settings import settings
import json
import os
import logging

logger = logging.getLogger(__name__)

class Blockchain:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(settings.RPC_URL))
        
        # Verificar conexão com Besu
        if not self.web3.is_connected():
            raise ConnectionError(f"Não foi possível conectar ao Besu em {settings.RPC_URL}")
        
        # Configurar conta
        self.account = self.web3.eth.account.from_key(settings.OWNER_PRIVATE_KEY)
        self.web3.eth.default_account = self.account.address
        
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
        
        logger.info(f"Conectado ao Besu. Conta: {self.account.address}")
        logger.info(f"Contrato: {settings.CONTRACT_ADDRESS}")

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
        """Obtém o preço do gas atual"""
        return self.web3.eth.gas_price

    def estimate_gas(self, function_call):
        """Estima o gas necessário para uma transação"""
        try:
            return function_call.estimate_gas()
        except ContractLogicError as e:
            logger.error(f"Erro ao estimar gas: {e}")
            raise

    def get_nonce(self):
        """Obtém o nonce atual da conta"""
        return self.web3.eth.get_transaction_count(self.account.address)

    def build_transaction(self, function_call, gas_limit=None):
        """Constrói uma transação para Besu"""
        gas_price = self.get_gas_price()
        nonce = self.get_nonce()
        
        tx_params = {
            'from': self.account.address,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': settings.CHAIN_ID
        }
        
        if gas_limit:
            tx_params['gas'] = gas_limit
        else:
            try:
                tx_params['gas'] = self.estimate_gas(function_call)
            except Exception:
                tx_params['gas'] = 3000000  # Gas limit padrão para Besu
        
        return function_call.build_transaction(tx_params)

    def send_transaction(self, function_call, gas_limit=None):
        """Envia uma transação para o Besu"""
        try:
            # Construir transação
            tx = self.build_transaction(function_call, gas_limit)
            
            # Assinar transação
            signed_tx = self.web3.eth.account.sign_transaction(tx, settings.OWNER_PRIVATE_KEY)
            
            # Enviar transação
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Aguardar confirmação
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            logger.info(f"Transação enviada: {tx_hash.hex()}")
            return receipt
            
        except Exception as e:
            logger.error(f"Erro ao enviar transação: {e}")
            raise

    def call_function(self, function_call):
        """Executa uma chamada de função (view/pure)"""
        try:
            return function_call.call()
        except ContractLogicError as e:
            logger.error(f"Erro na chamada da função: {e}")
            raise

    # Funções SAS-SAS
    def registration(self, payload: str):
        """Executa operação SAS-SAS Registration"""
        try:
            tx = self.contract.functions.registration(payload)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação registration: {e}")
            raise

    def grant(self, payload: str):
        """Executa operação SAS-SAS Grant"""
        try:
            tx = self.contract.functions.grant(payload)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação grant: {e}")
            raise

    def heartbeat(self, payload: str):
        """Executa operação SAS-SAS Heartbeat"""
        try:
            tx = self.contract.functions.heartbeat(payload)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação heartbeat: {e}")
            raise

    def relinquishment(self, payload: str):
        """Executa operação SAS-SAS Relinquishment"""
        try:
            tx = self.contract.functions.relinquishment(payload)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação relinquishment: {e}")
            raise

    def deregistration(self, payload: str):
        """Executa operação SAS-SAS Deregistration"""
        try:
            tx = self.contract.functions.deregistration(payload)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro na operação deregistration: {e}")
            raise

    # Funções de autorização SAS
    def authorize_sas(self, sas_address: str):
        """Autoriza um endereço como SAS"""
        try:
            tx = self.contract.functions.authorizeSAS(sas_address)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro ao autorizar SAS {sas_address}: {e}")
            raise

    def revoke_sas(self, sas_address: str):
        """Revoga autorização de um SAS"""
        try:
            tx = self.contract.functions.revokeSAS(sas_address)
            return self.send_transaction(tx)
        except Exception as e:
            logger.error(f"Erro ao revogar SAS {sas_address}: {e}")
            raise

    def is_authorized_sas(self, sas_address: str):
        """Verifica se um endereço é um SAS autorizado"""
        try:
            return self.contract.functions.authorizedSAS(sas_address).call()
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