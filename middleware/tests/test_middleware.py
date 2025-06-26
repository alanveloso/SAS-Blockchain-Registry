#!/usr/bin/env python3
"""
Script de teste para o middleware SASSharedRegistry
"""

import os
import sys
import asyncio
import pytest
from src.blockchain.blockchain import Blockchain
from src.repository.repository import CBSDRepository
from src.config.settings import settings
import json

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    
    try:
        from src.config.settings import settings
        print("✅ Config importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar config: {e}")
        return False
    
    try:
        from src.blockchain.blockchain import Blockchain
        print("✅ Blockchain importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar blockchain: {e}")
        return False
    
    try:
        from src.handlers.handlers import EVENT_HANDLERS
        print("✅ Handlers importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar handlers: {e}")
        return False
    
    try:
        from src.repository.repository import CBSDRepository
        print("✅ Repository importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar repository: {e}")
        return False
    
    return True

def test_config():
    """Testa se as configurações estão definidas"""
    print("\n🔧 Testando configurações...")
    
    try:
        from src.config.settings import settings
        
        # Verificar se as variáveis de ambiente estão definidas
        required_vars = ['RPC_URL', 'CONTRACT_ADDRESS', 'OWNER_PRIVATE_KEY', 'CHAIN_ID']
        
        for var in required_vars:
            if hasattr(settings, var):
                value = getattr(settings, var)
                if value:
                    print(f"✅ {var}: {str(value)[:20]}...")
                else:
                    print(f"⚠️  {var}: vazio")
            else:
                print(f"❌ {var}: não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar configurações: {e}")
        return False

def test_abi():
    """Testa se o ABI está presente"""
    print("\n📄 Testando ABI...")
    
    abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'SASSharedRegistry.json')
    
    if os.path.exists(abi_path):
        print(f"✅ ABI encontrado em: {abi_path}")
        
        try:
            import json
            with open(abi_path, 'r') as f:
                abi = json.load(f)
            print(f"✅ ABI carregado com sucesso ({len(abi)} itens)")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar ABI: {e}")
            return False
    else:
        print(f"❌ ABI não encontrado em: {abi_path}")
        return False

@pytest.mark.order(1)
def test_blockchain_connection():
    """Testa conexão com blockchain"""
    blockchain = Blockchain()
    
    # Verificar se consegue conectar
    assert blockchain.web3.is_connected()
    
    # Verificar se tem contrato configurado
    assert blockchain.contract is not None

@pytest.mark.order(2)
def test_sas_authorization():
    """Testa autorização de SAS"""
    blockchain = Blockchain()
    
    # Testar autorização
    sas_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    result = blockchain.authorize_sas(sas_address)
    assert result is not None
    
    # Verificar se está autorizado
    is_authorized = blockchain.is_authorized_sas(sas_address)
    assert is_authorized is True

@pytest.mark.order(3)
def test_sas_revocation():
    """Testa revogação de SAS"""
    blockchain = Blockchain()
    
    # Testar revogação
    sas_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    result = blockchain.revoke_sas(sas_address)
    assert result is not None
    
    # Verificar se foi revogado
    is_authorized = blockchain.is_authorized_sas(sas_address)
    assert is_authorized is False

@pytest.mark.order(4)
def test_registration():
    """Testa registration SAS-SAS"""
    blockchain = Blockchain()
    
    # Primeiro autorizar SAS
    sas_address = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    blockchain.authorize_sas(sas_address)
    
    # Payload de registration como JSON string
    payload = json.dumps({
        "fccId": "TEST-FCC-MIDDLEWARE",
        "userId": "TEST-USER-MIDDLEWARE",
        "cbsdSerialNumber": "TEST-SN-MIDDLEWARE",
        "callSign": "TESTCALL",
        "cbsdCategory": "A",
        "airInterface": "E_UTRA",
        "measCapability": ["EUTRA_CARRIER_RSSI"],
        "eirpCapability": 47,
        "latitude": 375000000,
        "longitude": 1224000000,
        "height": 30,
        "heightType": "AGL",
        "indoorDeployment": False,
        "antennaGain": 15,
        "antennaBeamwidth": 360,
        "antennaAzimuth": 0,
        "groupingParam": "",
        "cbsdAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
    })
    
    result = blockchain.registration(payload)
    assert result is not None

@pytest.mark.order(5)
def test_grant():
    """Testa grant SAS-SAS"""
    blockchain = Blockchain()
    
    # Payload de grant como JSON string
    payload = json.dumps({
        "fccId": "TEST-FCC-MIDDLEWARE",
        "cbsdSerialNumber": "TEST-SN-MIDDLEWARE",
        "channelType": "GAA",
        "maxEirp": 47,
        "lowFrequency": 3550000000,
        "highFrequency": 3700000000,
        "requestedMaxEirp": 47,
        "requestedLowFrequency": 3550000000,
        "requestedHighFrequency": 3700000000,
        "grantExpireTime": 1750726000
    })
    
    result = blockchain.grant(payload)
    assert result is not None

@pytest.mark.order(6)
def test_heartbeat():
    """Testa heartbeat SAS-SAS"""
    blockchain = Blockchain()
    
    # Payload de heartbeat como JSON string
    payload = json.dumps({
        "fccId": "TEST-FCC-MIDDLEWARE",
        "cbsdSerialNumber": "TEST-SN-MIDDLEWARE",
        "grantId": "grant_001",
        "transmitExpireTime": 1750726000
    })
    
    result = blockchain.heartbeat(payload)
    assert result is not None

@pytest.mark.order(7)
def test_relinquishment():
    """Testa relinquishment SAS-SAS"""
    blockchain = Blockchain()
    
    # Payload de relinquishment como JSON string
    payload = json.dumps({
        "fccId": "TEST-FCC-MIDDLEWARE",
        "cbsdSerialNumber": "TEST-SN-MIDDLEWARE",
        "grantId": "grant_001"
    })
    
    result = blockchain.relinquishment(payload)
    assert result is not None

@pytest.mark.order(8)
def test_deregistration():
    """Testa deregistration SAS-SAS"""
    blockchain = Blockchain()
    
    # Payload de deregistration como JSON string
    payload = json.dumps({
        "fccId": "TEST-FCC-MIDDLEWARE",
        "cbsdSerialNumber": "TEST-SN-MIDDLEWARE"
    })
    
    result = blockchain.deregistration(payload)
    assert result is not None

@pytest.mark.order(9)
def test_get_latest_block():
    """Testa obtenção do último bloco"""
    blockchain = Blockchain()
    
    block_number = blockchain.get_latest_block()
    assert isinstance(block_number, int)
    assert block_number > 0

@pytest.mark.order(10)
def test_get_owner():
    """Testa obtenção do owner do contrato"""
    blockchain = Blockchain()
    
    owner = blockchain.get_owner()
    assert isinstance(owner, str)
    assert len(owner) == 42  # Endereço Ethereum

@pytest.mark.order(11)
def test_unauthorized_sas_access():
    """Testa acesso de SAS não autorizado"""
    blockchain = Blockchain()
    
    # Tentar operação com SAS não autorizado
    unauthorized_sas = "0x1234567890123456789012345678901234567890"
    
    # Verificar que não está autorizado
    is_authorized = blockchain.is_authorized_sas(unauthorized_sas)
    assert is_authorized is False

@pytest.mark.order(12)
def test_repository_operations():
    """Testa operações do repositório"""
    repo = CBSDRepository()
    
    # Testar adição de CBSD
    cbsd_data = {
        "fccId": "TEST-FCC-REPO",
        "serialNumber": "TEST-SN-REPO",
        "status": "active"
    }
    
    cbsd_id = "TEST-FCC-REPO-TEST-SN-REPO"
    repo.add(cbsd_id, cbsd_data)
    
    # Verificar se foi adicionado
    retrieved = repo.get(cbsd_id)
    assert retrieved is not None
    assert retrieved["fccId"] == "TEST-FCC-REPO"
    
    # Testar listagem
    all_cbsds = repo.all()
    assert len(all_cbsds) > 0

@pytest.mark.order(13)
def test_settings_configuration():
    """Testa configuração de settings"""
    # Verificar campos obrigatórios
    assert hasattr(settings, 'RPC_URL')
    assert hasattr(settings, 'CONTRACT_ADDRESS')
    assert hasattr(settings, 'OWNER_PRIVATE_KEY')
    
    # Verificar que os valores não estão vazios
    assert settings.RPC_URL is not None
    assert settings.CONTRACT_ADDRESS is not None
    assert settings.OWNER_PRIVATE_KEY is not None 