#!/usr/bin/env python3
"""
Script para testar o middleware simulando eventos do contrato
"""
import asyncio
import json
import time
from datetime import datetime
from handlers import EVENT_HANDLERS

def create_mock_event(event_name, **kwargs):
    """Cria um evento mock para teste"""
    base_event = {
        'blockNumber': int(time.time()),
        'transactionHash': f"0x{hash(event_name + str(time.time())):064x}",
        'args': kwargs
    }
    return base_event

async def test_middleware_handlers():
    """Testa todos os handlers do middleware"""
    print("🧪 Testando handlers do middleware...")
    
    # Teste 1: SASAuthorized
    print("\n🔐 Testando SASAuthorized...")
    sas_event = create_mock_event('SASAuthorized', sas='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['SASAuthorized'](sas_event)
    
    # Teste 2: CBSDRegistered
    print("\n📡 Testando CBSDRegistered...")
    cbsd_event = create_mock_event('CBSDRegistered', 
                                  cbsdId=1, 
                                  sasOrigin='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['CBSDRegistered'](cbsd_event)
    
    # Teste 3: GrantAmountUpdated
    print("\n💰 Testando GrantAmountUpdated...")
    grant_event = create_mock_event('GrantAmountUpdated',
                                   cbsdId=1,
                                   newGrantAmount=150000000000000000000,  # 150 ETH
                                   sasOrigin='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['GrantAmountUpdated'](grant_event)
    
    # Teste 4: StatusUpdated
    print("\n📊 Testando StatusUpdated...")
    status_event = create_mock_event('StatusUpdated',
                                    cbsdId=1,
                                    newStatus='active',
                                    sasOrigin='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['StatusUpdated'](status_event)
    
    # Teste 5: GrantDetailsUpdated
    print("\n⚙️ Testando GrantDetailsUpdated...")
    details_event = create_mock_event('GrantDetailsUpdated',
                                     cbsdId=1,
                                     frequencyHz=3650000000,  # 3.65 GHz
                                     bandwidthHz=20000000,    # 20 MHz
                                     expiryTimestamp=int(time.time()) + 7200,
                                     sasOrigin='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['GrantDetailsUpdated'](details_event)
    
    # Teste 6: SASRevoked
    print("\n🚫 Testando SASRevoked...")
    revoke_event = create_mock_event('SASRevoked', sas='0x70997970C51812dc3A010C7d01b50e0d17dc79C8')
    EVENT_HANDLERS['SASRevoked'](revoke_event)
    
    print("\n✅ Todos os handlers testados com sucesso!")
    
    # Mostrar dados do repositório
    from repository import CBSDRepository
    repo = CBSDRepository()
    print(f"\n📋 Dados no repositório: {len(repo.cbsds)} registros")
    for cbsd_id, data in repo.cbsds.items():
        print(f"  CBSD {cbsd_id}: {data}")

if __name__ == "__main__":
    asyncio.run(test_middleware_handlers()) 