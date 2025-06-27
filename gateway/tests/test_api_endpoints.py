import pytest
from fastapi.testclient import TestClient
from api.api import app
from blockchain.blockchain import Blockchain
import json

# Inicializar blockchain manualmente para os testes
try:
    blockchain = Blockchain()
    # Substituir o objeto global na API
    import api.api as api_module
    api_module.blockchain = blockchain
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
def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()
    assert "SAS-SAS" in resp.json()["message"]

@pytest.mark.order(2)
def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.order(3)
def test_authorize_sas():
    resp = client.post("/sas/authorize", json={"sas_address": SAS_ADDRESS})
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(4)
def test_check_sas_authorized():
    resp = client.get(f"/sas/{SAS_ADDRESS}/authorized")
    assert resp.status_code == 200
    assert resp.json()["authorized"] is True

@pytest.mark.order(5)
def test_register_cbsd():
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
    assert resp.json()["success"] is True

@pytest.mark.order(6)
def test_grant_spectrum():
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
    assert resp.json()["success"] is True

@pytest.mark.order(8)
def test_relinquishment():
    relinquishment_payload = {
        "fccId": FCC_ID,
        "cbsdSerialNumber": CBSD_SERIAL,
        "grantId": "grant_001"
    }
    resp = client.post("/v1.3/relinquishment", json=relinquishment_payload)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(9)
def test_deregistration():
    deregistration_payload = {
        "fccId": FCC_ID,
        "cbsdSerialNumber": CBSD_SERIAL
    }
    resp = client.post("/v1.3/deregistration", json=deregistration_payload)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(10)
def test_stats():
    resp = client.get("/stats")
    assert resp.status_code == 200
    assert "owner" in resp.json()
    assert "contract_address" in resp.json()
    assert "version" in resp.json()

@pytest.mark.order(11)
def test_events_recent():
    resp = client.get("/events/recent")
    assert resp.status_code == 200
    assert "events" in resp.json()
    assert "total" in resp.json()

@pytest.mark.order(12)
def test_revoke_sas():
    resp = client.post("/sas/revoke", json={"sas_address": SAS_ADDRESS})
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(13)
def test_check_sas_revoked():
    resp = client.get(f"/sas/{SAS_ADDRESS}/authorized")
    assert resp.status_code == 200
    assert resp.json()["authorized"] is False 