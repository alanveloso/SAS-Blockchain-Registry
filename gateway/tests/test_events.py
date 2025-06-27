import pytest
from fastapi.testclient import TestClient
from api.api import app
from blockchain.blockchain import Blockchain
import json

# Inicializar blockchain manualmente para os testes
try:
    blockchain = Blockchain()
    # Substituir o objeto global na API
    # import api.api as api_module
    # api_module.blockchain = blockchain
except Exception as e:
    print(f"Erro ao inicializar blockchain para testes: {e}")
    blockchain = None

client = TestClient(app)

# Dados de exemplo
SAS_ADDRESS = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
FCC_ID = "TEST-FCC-EVENTS"
USER_ID = "TEST-USER-EVENTS"
CBSD_SERIAL = "TEST-SN-EVENTS"

@pytest.mark.order(1)
def test_events_recent_empty():
    """Testa eventos recentes quando não há eventos"""
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert "total" in data
    assert isinstance(data["events"], list)
    assert isinstance(data["total"], int)

@pytest.mark.order(2)
def test_events_after_registration():
    """Testa eventos após registration"""
    # Fazer registration
    reg_payload = {
        "fccId": FCC_ID,
        "userId": USER_ID,
        "cbsdSerialNumber": CBSD_SERIAL,
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
    }
    
    resp = client.post("/v1.3/registration", json=reg_payload)
    assert resp.status_code == 200
    
    # Verificar eventos
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    
    # Verificar se há evento de Registration
    registration_events = [e for e in data["events"] if e["event"] == "CBSDRegistered"]
    assert len(registration_events) > 0
    for event in registration_events:
        assert "sasOrigin" in event
        assert "fccId" in event
        assert "serialNumber" in event
        assert "timestamp" in event

@pytest.mark.order(3)
def test_events_after_grant():
    """Testa eventos após grant"""
    # Fazer grant
    grant_payload = {
        "fccId": FCC_ID,
        "cbsdSerialNumber": CBSD_SERIAL,
        "channelType": "GAA",
        "maxEirp": 47,
        "lowFrequency": 3550000000,
        "highFrequency": 3700000000,
        "requestedMaxEirp": 47,
        "requestedLowFrequency": 3550000000,
        "requestedHighFrequency": 3700000000,
        "grantExpireTime": 1750726000
    }
    
    resp = client.post("/v1.3/grant", json=grant_payload)
    assert resp.status_code == 200
    
    # Verificar eventos
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar se há evento de Grant
    grant_events = [e for e in data["events"] if e["event"] == "GrantCreated"]
    assert len(grant_events) > 0
    for event in grant_events:
        assert "sasOrigin" in event
        assert "fccId" in event
        assert "serialNumber" in event
        assert "grantId" in event
        assert "timestamp" in event

@pytest.mark.order(4)
def test_events_after_relinquishment():
    """Testa eventos após relinquishment"""
    # Buscar o grantId criado no teste anterior
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    grant_events = [e for e in data["events"] if e["event"] == "GrantCreated"]
    assert len(grant_events) > 0
    grant_id = grant_events[0]["grantId"]

    # Fazer relinquishment com o grantId correto
    relinquishment_payload = {
        "fccId": FCC_ID,
        "cbsdSerialNumber": CBSD_SERIAL,
        "grantId": grant_id
    }
    resp = client.post("/v1.3/relinquishment", json=relinquishment_payload)
    assert resp.status_code == 200

    # Verificar eventos
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()

    # Verificar se há evento de Relinquishment
    relinquishment_events = [e for e in data["events"] if e["event"] == "GrantTerminated"]
    assert len(relinquishment_events) > 0
    for event in relinquishment_events:
        assert "sasOrigin" in event
        assert "fccId" in event
        assert "serialNumber" in event
        assert "grantId" in event
        assert "timestamp" in event

@pytest.mark.order(5)
def test_events_after_sas_authorization():
    """Testa eventos após autorização de SAS"""
    # Autorizar SAS
    resp = client.post("/sas/authorize", json={"sas_address": SAS_ADDRESS})
    assert resp.status_code == 200
    
    # Verificar eventos
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar se há evento de SASAuthorized
    sas_authorized_events = [e for e in data["events"] if e["event"] == "SASAuthorized"]
    assert len(sas_authorized_events) > 0

@pytest.mark.order(6)
def test_events_after_sas_revocation():
    """Testa eventos após revogação de SAS"""
    # Revogar SAS
    resp = client.post("/sas/revoke", json={"sas_address": SAS_ADDRESS})
    assert resp.status_code == 200
    
    # Verificar eventos
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    
    # Verificar se há evento de SASRevoked
    sas_revoked_events = [e for e in data["events"] if e["event"] == "SASRevoked"]
    assert len(sas_revoked_events) > 0

@pytest.mark.order(7)
def test_event_structure():
    """Testa a estrutura dos eventos"""
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    data = resp.json()
    
    if data["total"] > 0:
        event = data["events"][0]
        
        # Verificar campos obrigatórios
        assert "event" in event
        assert "block_number" in event
        assert "transaction_hash" in event
        
        # Verificar campos específicos por tipo de evento
        if event["event"] in ["CBSDRegistered", "GrantCreated", "GrantTerminated"]:
            assert "sasOrigin" in event
            assert "timestamp" in event
        elif event["event"] in ["SASAuthorized", "SASRevoked"]:
            assert "sas" in event 