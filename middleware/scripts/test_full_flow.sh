#!/bin/bash
set -e
set -o pipefail

API_URL="http://localhost:8000"
FCC_ID="TEST-FCC-ID"
USER_ID="TEST-USER-ID"
CBSD_SERIAL="TEST-CBSD-SERIAL"
CALL_SIGN="TESTCALL"
CBSD_CATEGORY="A"
AIR_INTERFACE="E_UTRA"
MEAS_CAPABILITY='["EUTRA_CARRIER_RSSI"]'
EIRP_CAPABILITY=47
LATITUDE=10
LONGITUDE=20
HEIGHT=5
HEIGHT_TYPE="AGL"
INDOOR_DEPLOYMENT=false
ANTENNA_GAIN=10
ANTENNA_BEAMWIDTH=90
ANTENNA_AZIMUTH=0
GROUPING_PARAM="GROUP1"
CBSD_ADDRESS="192.168.0.1"
CHANNEL_TYPE="GAA"
MAX_EIRP=30
LOW_FREQ=3550000000
HIGH_FREQ=3560000000

# 1. Health Check
echo "\n== Health Check =="
curl -s $API_URL/health | jq .

# 2. Autorizar FCC ID
echo "\n== Autorizar FCC ID =="
curl -s -X POST $API_URL/v1.3/admin/injectFccId \
  -H "Content-Type: application/json" \
  -d '{"fccId": "'$FCC_ID'", "maxEirp": 47}' | jq .

# 3. Autorizar User ID
echo "\n== Autorizar User ID =="
curl -s -X POST $API_URL/v1.3/admin/injectUserId \
  -H "Content-Type: application/json" \
  -d '{"userId": "'$USER_ID'"}' | jq .

# 4. Registrar CBSD
echo "\n== Registrar CBSD =="
curl -s -X POST $API_URL/v1.3/registration \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "'$FCC_ID'",
    "userId": "'$USER_ID'",
    "cbsdSerialNumber": "'$CBSD_SERIAL'",
    "callSign": "'$CALL_SIGN'",
    "cbsdCategory": "'$CBSD_CATEGORY'",
    "airInterface": "'$AIR_INTERFACE'",
    "measCapability": ["EUTRA_CARRIER_RSSI"],
    "eirpCapability": '$EIRP_CAPABILITY',
    "latitude": '$LATITUDE',
    "longitude": '$LONGITUDE',
    "height": '$HEIGHT',
    "heightType": "'$HEIGHT_TYPE'",
    "indoorDeployment": '$INDOOR_DEPLOYMENT',
    "antennaGain": '$ANTENNA_GAIN',
    "antennaBeamwidth": '$ANTENNA_BEAMWIDTH',
    "antennaAzimuth": '$ANTENNA_AZIMUTH',
    "groupingParam": "'$GROUPING_PARAM'",
    "cbsdAddress": "'$CBSD_ADDRESS'"
  }' | jq .

# 5. Solicitar Grant (expiração futura)
FUTURE=$(($(date +%s) + 3600))
echo "\n== Solicitar Grant (expiração futura) =="
curl -s -X POST $API_URL/v1.3/grant \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "'$FCC_ID'",
    "cbsdSerialNumber": "'$CBSD_SERIAL'",
    "channelType": "'$CHANNEL_TYPE'",
    "maxEirp": '$MAX_EIRP',
    "lowFrequency": '$LOW_FREQ',
    "highFrequency": '$HIGH_FREQ',
    "requestedMaxEirp": '$MAX_EIRP',
    "requestedLowFrequency": '$LOW_FREQ',
    "requestedHighFrequency": '$HIGH_FREQ',
    "grantExpireTime": '$FUTURE'
  }' | jq .

# 6. Consultar CBSD e extrair grantId
echo "\n== Consultar CBSD e extrair grantId =="
CBSD_JSON=$(curl -s $API_URL/cbsd/$FCC_ID/$CBSD_SERIAL)
echo "$CBSD_JSON" | jq .
# Extrai o grantId exatamente como retornado, escapando para JSON
GRANT_ID=$(echo "$CBSD_JSON" | jq -r '.grants[-1].grantId | @json')
echo "GrantId extraído: $GRANT_ID"

# 7. Enviar Heartbeat
echo "\n== Enviar Heartbeat =="
curl -s -X POST $API_URL/v1.3/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "'$FCC_ID'",
    "cbsdSerialNumber": "'$CBSD_SERIAL'",
    "grantId": '$GRANT_ID'
  }' | jq .

echo "\n== Fluxo completo executado com sucesso! ==" 