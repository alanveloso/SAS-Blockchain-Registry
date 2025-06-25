import pytest
from fastapi.testclient import TestClient
from src.api.api import app

client = TestClient(app)

# Dados de exemplo
SAS_ADDRESS = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
FCC_ID = "TEST-FCC-ID"
USER_ID = "TEST-USER-ID"
CBSD_SERIAL = "TEST-CBSD-SERIAL"
CALL_SIGN = "TESTCALL"
CBSD_CATEGORY = "A"
AIR_INTERFACE = "E_UTRA"
MEAS_CAPABILITY = ["EUTRA_CARRIER_RSSI"]
EIRP_CAPABILITY = 47
LATITUDE = 10
LONGITUDE = 20
HEIGHT = 5
HEIGHT_TYPE = "AGL"
INDOOR_DEPLOYMENT = False
ANTENNA_GAIN = 10
ANTENNA_BEAMWIDTH = 90
ANTENNA_AZIMUTH = 0
GROUPING_PARAM = "GROUP1"
CBSD_ADDRESS = "192.168.0.1"

@pytest.mark.order(1)
def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()

@pytest.mark.order(2)
def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

@pytest.mark.order(3)
def test_authorize_sas():
    resp = client.post("/v1.3/admin/authorize", json={"sas_address": SAS_ADDRESS})
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
        "callSign": CALL_SIGN,
        "cbsdCategory": CBSD_CATEGORY,
        "airInterface": AIR_INTERFACE,
        "measCapability": MEAS_CAPABILITY,
        "eirpCapability": EIRP_CAPABILITY,
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "height": HEIGHT,
        "heightType": HEIGHT_TYPE,
        "indoorDeployment": INDOOR_DEPLOYMENT,
        "antennaGain": ANTENNA_GAIN,
        "antennaBeamwidth": ANTENNA_BEAMWIDTH,
        "antennaAzimuth": ANTENNA_AZIMUTH,
        "groupingParam": GROUPING_PARAM,
        "cbsdAddress": CBSD_ADDRESS
    }
    resp = client.post("/v1.3/registration", json=reg_payload)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(6)
def test_get_cbsd_info():
    resp = client.get(f"/cbsd/{FCC_ID}/{CBSD_SERIAL}")
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert resp.json()["cbsd"]["fccId"] == FCC_ID
    assert resp.json()["cbsd"]["serialNumber"] == CBSD_SERIAL

@pytest.mark.order(7)
def test_is_cbsd_registered():
    resp = client.get(f"/cbsd/{FCC_ID}/{CBSD_SERIAL}/registered")
    assert resp.status_code == 200
    assert resp.json()["registered"] is True

@pytest.mark.order(8)
def test_revoke_sas():
    resp = client.post("/v1.3/admin/revoke", json={"sas_address": SAS_ADDRESS})
    assert resp.status_code == 200
    assert resp.json()["success"] is True

@pytest.mark.order(9)
def test_check_sas_revoked():
    resp = client.get(f"/sas/{SAS_ADDRESS}/authorized")
    assert resp.status_code == 200
    assert resp.json()["authorized"] is False 