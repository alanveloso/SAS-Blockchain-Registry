import logging
from typing import Dict, Any
from repository import CBSDRepository

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância global do repositório
repo = CBSDRepository()

def handle_sas_authorized(event: Dict[str, Any]):
    """Handler para evento SASAuthorized"""
    logger.info(f"SAS autorizado: {event['args']['sas']}")
    # Adicione lógica específica para SAS autorizado

def handle_sas_revoked(event: Dict[str, Any]):
    """Handler para evento SASRevoked"""
    logger.info(f"SAS revogado: {event['args']['sas']}")
    # Adicione lógica específica para SAS revogado

def handle_cbsd_registered(event: Dict[str, Any]):
    """Handler para evento CBSDRegistered"""
    cbsd_id = event['args']['cbsdId']
    sas_origin = event['args']['sasOrigin']
    logger.info(f"Novo CBSD registrado - ID: {cbsd_id}, SAS Origin: {sas_origin}")
    
    # Armazenar no repositório
    repo.add(cbsd_id, {
        'id': cbsd_id,
        'sas_origin': sas_origin,
        'status': 'registered',
        'block_number': event['blockNumber'],
        'transaction_hash': event['transactionHash']
    })

def handle_grant_amount_updated(event: Dict[str, Any]):
    """Handler para evento GrantAmountUpdated"""
    cbsd_id = event['args']['cbsdId']
    new_grant_amount = event['args']['newGrantAmount']
    sas_origin = event['args']['sasOrigin']
    logger.info(f"Grant amount atualizado - CBSD ID: {cbsd_id}, Novo valor: {new_grant_amount}, SAS: {sas_origin}")
    
    # Atualizar no repositório
    cbsd_data = repo.get(cbsd_id)
    if cbsd_data:
        cbsd_data['grant_amount'] = new_grant_amount
        cbsd_data['last_update'] = event['blockNumber']
        repo.add(cbsd_id, cbsd_data)

def handle_status_updated(event: Dict[str, Any]):
    """Handler para evento StatusUpdated"""
    cbsd_id = event['args']['cbsdId']
    new_status = event['args']['newStatus']
    sas_origin = event['args']['sasOrigin']
    logger.info(f"Status atualizado - CBSD ID: {cbsd_id}, Novo status: {new_status}, SAS: {sas_origin}")
    
    # Atualizar no repositório
    cbsd_data = repo.get(cbsd_id)
    if cbsd_data:
        cbsd_data['status'] = new_status
        cbsd_data['last_update'] = event['blockNumber']
        repo.add(cbsd_id, cbsd_data)

def handle_grant_details_updated(event: Dict[str, Any]):
    """Handler para evento GrantDetailsUpdated"""
    cbsd_id = event['args']['cbsdId']
    frequency_hz = event['args']['frequencyHz']
    bandwidth_hz = event['args']['bandwidthHz']
    expiry_timestamp = event['args']['expiryTimestamp']
    sas_origin = event['args']['sasOrigin']
    
    logger.info(f"Detalhes do grant atualizados - CBSD ID: {cbsd_id}, "
                f"Freq: {frequency_hz}Hz, BW: {bandwidth_hz}Hz, "
                f"Expiry: {expiry_timestamp}, SAS: {sas_origin}")
    
    # Atualizar no repositório
    cbsd_data = repo.get(cbsd_id)
    if cbsd_data:
        cbsd_data.update({
            'frequency_hz': frequency_hz,
            'bandwidth_hz': bandwidth_hz,
            'expiry_timestamp': expiry_timestamp,
            'last_update': event['blockNumber']
        })
        repo.add(cbsd_id, cbsd_data)

# Mapeamento de eventos para handlers
EVENT_HANDLERS = {
    'SASAuthorized': handle_sas_authorized,
    'SASRevoked': handle_sas_revoked,
    'CBSDRegistered': handle_cbsd_registered,
    'GrantAmountUpdated': handle_grant_amount_updated,
    'StatusUpdated': handle_status_updated,
    'GrantDetailsUpdated': handle_grant_details_updated
} 