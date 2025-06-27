import logging
from typing import Dict, Any
from repository.repository import CBSDRepository

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Instância global do repositório
repo = CBSDRepository()

def handle_sas_authorized(event: Dict[str, Any]):
    """Handler para evento SASAuthorized"""
    sas_address = event['args']['sas']
    logger.info(f"SAS autorizado: {sas_address}")
    # Adicione lógica específica para SAS autorizado

def handle_sas_revoked(event: Dict[str, Any]):
    """Handler para evento SASRevoked"""
    sas_address = event['args']['sas']
    logger.info(f"SAS revogado: {sas_address}")
    # Adicione lógica específica para SAS revogado

def handle_cbsd_registered(event: Dict[str, Any]):
    """Handler para evento CBSDRegistered"""
    fcc_id = event['args']['fccId']
    serial_number = event['args']['serialNumber']
    sas_origin = event['args']['sasOrigin']
    
    # Gerar ID único do CBSD (fccId + serialNumber)
    cbsd_id = f"{fcc_id}_{serial_number}"
    
    logger.info(f"Novo CBSD registrado - FCC ID: {fcc_id}, Serial: {serial_number}, SAS Origin: {sas_origin}")
    
    # Armazenar no repositório
    repo.add(cbsd_id, {
        'fcc_id': fcc_id,
        'serial_number': serial_number,
        'sas_origin': sas_origin,
        'status': 'registered',
        'block_number': event['blockNumber'],
        'transaction_hash': event['transactionHash']
    })

def handle_grant_created(event: Dict[str, Any]):
    """Handler para evento GrantCreated"""
    fcc_id = event['args']['fccId']
    serial_number = event['args']['serialNumber']
    grant_id = event['args']['grantId']
    sas_origin = event['args']['sasOrigin']
    
    cbsd_id = f"{fcc_id}_{serial_number}"
    
    logger.info(f"Novo grant criado - FCC ID: {fcc_id}, Serial: {serial_number}, "
                f"Grant ID: {grant_id}, SAS: {sas_origin}")
    
    # Atualizar no repositório
    cbsd_data = repo.get(cbsd_id)
    if cbsd_data:
        if 'grants' not in cbsd_data:
            cbsd_data['grants'] = []
        
        cbsd_data['grants'].append({
            'grant_id': grant_id,
            'sas_origin': sas_origin,
            'created_at': event['blockNumber'],
            'transaction_hash': event['transactionHash']
        })
        repo.add(cbsd_id, cbsd_data)

def handle_grant_terminated(event: Dict[str, Any]):
    """Handler para evento GrantTerminated"""
    fcc_id = event['args']['fccId']
    serial_number = event['args']['serialNumber']
    grant_id = event['args']['grantId']
    sas_origin = event['args']['sasOrigin']
    
    cbsd_id = f"{fcc_id}_{serial_number}"
    
    logger.info(f"Grant terminado - FCC ID: {fcc_id}, Serial: {serial_number}, "
                f"Grant ID: {grant_id}, SAS: {sas_origin}")
    
    # Atualizar no repositório
    cbsd_data = repo.get(cbsd_id)
    if cbsd_data and 'grants' in cbsd_data:
        for grant in cbsd_data['grants']:
            if grant['grant_id'] == grant_id:
                grant['terminated'] = True
                grant['terminated_at'] = event['blockNumber']
                grant['terminated_by'] = sas_origin
                break
        repo.add(cbsd_id, cbsd_data)

def handle_fcc_id_injected(event: Dict[str, Any]):
    """Handler para evento FCCIdInjected"""
    fcc_id = event['args']['fccId']
    max_eirp = event['args']['maxEirp']
    logger.info(f"FCC ID injetado: {fcc_id}, Max EIRP: {max_eirp}")

def handle_user_id_injected(event: Dict[str, Any]):
    """Handler para evento UserIdInjected"""
    user_id = event['args']['userId']
    logger.info(f"User ID injetado: {user_id}")

def handle_fcc_id_blacklisted(event: Dict[str, Any]):
    """Handler para evento FCCIdBlacklisted"""
    fcc_id = event['args']['fccId']
    logger.info(f"FCC ID blacklistado: {fcc_id}")

def handle_serial_number_blacklisted(event: Dict[str, Any]):
    """Handler para evento SerialNumberBlacklisted"""
    fcc_id = event['args']['fccId']
    serial_number = event['args']['serialNumber']
    logger.info(f"Serial number blacklistado - FCC ID: {fcc_id}, Serial: {serial_number}")

# Mapeamento de eventos para handlers
EVENT_HANDLERS = {
    'SASAuthorized': handle_sas_authorized,
    'SASRevoked': handle_sas_revoked,
    'CBSDRegistered': handle_cbsd_registered,
    'GrantCreated': handle_grant_created,
    'GrantTerminated': handle_grant_terminated,
    'FCCIdInjected': handle_fcc_id_injected,
    'UserIdInjected': handle_user_id_injected,
    'FCCIdBlacklisted': handle_fcc_id_blacklisted,
    'SerialNumberBlacklisted': handle_serial_number_blacklisted
} 