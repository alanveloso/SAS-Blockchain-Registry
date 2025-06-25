# SAS Shared Registry API Documentation

API REST para comunicação SAS-SAS via blockchain, permitindo que sistemas SAS se comuniquem usando requisições HTTP padrão.

## Iniciar a API

```bash
cd middleware
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

A API estará disponível em: `http://localhost:8000`

---

## Fluxo Completo Sugerido

1. **Health Check**
2. **Autorizar FCC ID**
3. **Autorizar User ID**
4. **Registrar CBSD**
5. **Solicitar Grant**
6. **Consultar CBSD**
7. **Enviar Heartbeat**

---

## Endpoints

### 1. Health Check
```bash
GET /health
```
**Resposta:**
```json
{
  "status": "healthy",
  "blockchain_connected": true,
  "latest_block": 21,
  "contract_address": "0x...",
  "total_cbsds": 1,
  "total_grants": 4
}
```

### 2. Autorizar FCC ID
```bash
POST /v1.3/admin/injectFccId
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "maxEirp": 47
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "FCC ID TEST-FCC-ID injetado",
  "transaction_hash": "...",
  "block_number": 13
}
```

### 3. Autorizar User ID
```bash
POST /v1.3/admin/injectUserId
```
**Body:**
```json
{
  "userId": "TEST-USER-ID"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "User ID TEST-USER-ID injetado",
  "transaction_hash": "...",
  "block_number": 14
}
```

### 4. Registrar CBSD
```bash
POST /v1.3/registration
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "userId": "TEST-USER-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "callSign": "TESTCALL",
  "cbsdCategory": "A",
  "airInterface": "E_UTRA",
  "measCapability": ["EUTRA_CARRIER_RSSI"],
  "eirpCapability": 47,
  "latitude": 10,
  "longitude": 20,
  "height": 5,
  "heightType": "AGL",
  "indoorDeployment": false,
  "antennaGain": 10,
  "antennaBeamwidth": 90,
  "antennaAzimuth": 0,
  "groupingParam": "GROUP1",
  "cbsdAddress": "192.168.0.1"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "CBSD registrado",
  "transaction_hash": "...",
  "block_number": 15
}
```

### 5. Solicitar Grant
```bash
POST /v1.3/grant
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "channelType": "GAA",
  "maxEirp": 30,
  "lowFrequency": 3550000000,
  "highFrequency": 3560000000,
  "requestedMaxEirp": 30,
  "requestedLowFrequency": 3550000000,
  "requestedHighFrequency": 3560000000,
  "grantExpireTime": 1750726000
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "Grant solicitado para TEST-FCC-ID/TEST-CBSD-SERIAL",
  "transaction_hash": "...",
  "block_number": 16
}
```

### 6. Consultar CBSD
```bash
GET /cbsd/TEST-FCC-ID/TEST-CBSD-SERIAL
```
**Resposta:**
```json
{
  "success": true,
  "cbsd": {
    "fccId": "TEST-FCC-ID",
    "serialNumber": "TEST-CBSD-SERIAL",
    "userId": "TEST-USER-ID",
    "callSign": "TESTCALL",
    "category": "A",
    "latitude": 10,
    "longitude": 20,
    "height": 5,
    "indoorDeployment": false,
    "antennaGain": 10,
    "cbsdAddress": "GROUP1",
    "sasOrigin": "192.168.0.1",
    "registrationTimestamp": "..."
  },
  "grants": [
    {
      "grantId": "grant_TEST-FCC-IDTEST-CBSD-SERIAL\u0000...",
      "channelType": "GAA",
      "maxEirp": 30,
      "lowFrequency": 3550000000,
      "highFrequency": 3560000000,
      "terminated": false,
      "expireTime": 1750726000
    }
  ]
}
```

### 7. Enviar Heartbeat
```bash
POST /v1.3/heartbeat
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "grantId": "grant_TEST-FCC-IDTEST-CBSD-SERIAL\u0000..."
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "Heartbeat enviado para grant ...",
  "transaction_hash": "...",
  "block_number": 21
}
```

---

## Exemplos de Uso com curl

```bash
# Health Check
curl http://localhost:8000/health

# Autorizar FCC ID
curl -X POST http://localhost:8000/v1.3/admin/injectFccId \
  -H "Content-Type: application/json" \
  -d '{"fccId": "TEST-FCC-ID", "maxEirp": 47}'

# Autorizar User ID
curl -X POST http://localhost:8000/v1.3/admin/injectUserId \
  -H "Content-Type: application/json" \
  -d '{"userId": "TEST-USER-ID"}'

# Registrar CBSD
curl -X POST http://localhost:8000/v1.3/registration \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "userId": "TEST-USER-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "callSign": "TESTCALL",
    "cbsdCategory": "A",
    "airInterface": "E_UTRA",
    "measCapability": ["EUTRA_CARRIER_RSSI"],
    "eirpCapability": 47,
    "latitude": 10,
    "longitude": 20,
    "height": 5,
    "heightType": "AGL",
    "indoorDeployment": false,
    "antennaGain": 10,
    "antennaBeamwidth": 90,
    "antennaAzimuth": 0,
    "groupingParam": "GROUP1",
    "cbsdAddress": "192.168.0.1"
  }'

# Solicitar Grant
curl -X POST http://localhost:8000/v1.3/grant \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "channelType": "GAA",
    "maxEirp": 30,
    "lowFrequency": 3550000000,
    "highFrequency": 3560000000,
    "requestedMaxEirp": 30,
    "requestedLowFrequency": 3550000000,
    "requestedHighFrequency": 3560000000,
    "grantExpireTime": 1750726000
  }'

# Consultar CBSD
curl http://localhost:8000/cbsd/TEST-FCC-ID/TEST-CBSD-SERIAL

# Enviar Heartbeat (use o grantId retornado na consulta do CBSD)
curl -X POST http://localhost:8000/v1.3/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "grantId": "grant_TEST-FCC-IDTEST-CBSD-SERIAL\u0000..."
  }'
```

---

## Exemplos de Uso em Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Health Check
print(requests.get(f"{BASE_URL}/health").json())

# Autorizar FCC ID
print(requests.post(f"{BASE_URL}/v1.3/admin/injectFccId", json={"fccId": "TEST-FCC-ID", "maxEirp": 47}).json())

# Autorizar User ID
print(requests.post(f"{BASE_URL}/v1.3/admin/injectUserId", json={"userId": "TEST-USER-ID"}).json())

# Registrar CBSD
print(requests.post(f"{BASE_URL}/v1.3/registration", json={
    "fccId": "TEST-FCC-ID",
    "userId": "TEST-USER-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "callSign": "TESTCALL",
    "cbsdCategory": "A",
    "airInterface": "E_UTRA",
    "measCapability": ["EUTRA_CARRIER_RSSI"],
    "eirpCapability": 47,
    "latitude": 10,
    "longitude": 20,
    "height": 5,
    "heightType": "AGL",
    "indoorDeployment": False,
    "antennaGain": 10,
    "antennaBeamwidth": 90,
    "antennaAzimuth": 0,
    "groupingParam": "GROUP1",
    "cbsdAddress": "192.168.0.1"
}).json())

# Solicitar Grant
print(requests.post(f"{BASE_URL}/v1.3/grant", json={
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "channelType": "GAA",
    "maxEirp": 30,
    "lowFrequency": 3550000000,
    "highFrequency": 3560000000,
    "requestedMaxEirp": 30,
    "requestedLowFrequency": 3550000000,
    "requestedHighFrequency": 3560000000,
    "grantExpireTime": 1750726000
}).json())

# Consultar CBSD
cbsd = requests.get(f"{BASE_URL}/cbsd/TEST-FCC-ID/TEST-CBSD-SERIAL").json()
print(cbsd)

grant_id = cbsd["grants"][-1]["grantId"]

# Enviar Heartbeat
print(requests.post(f"{BASE_URL}/v1.3/heartbeat", json={
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "grantId": grant_id
}).json())
```

---

## ⚙️ Configuração, Deploy, Logs e Segurança

### Variáveis de Ambiente
A API usa as mesmas variáveis do middleware:
- `RPC_URL`: URL do nó Besu
- `CONTRACT_ADDRESS`: Endereço do contrato
- `OWNER_PRIVATE_KEY`: Chave privada do owner
- `CHAIN_ID`: ID da rede

### CORS
A API está configurada para aceitar requisições de qualquer origem (`*`).

### Logs
A API gera logs detalhados de todas as operações:
- Requisições recebidas
- Transações enviadas
- Erros e exceções

## 🚀 Deploy

### Desenvolvimento
```bash
python3 run.py
```

### Produção
```bash
uvicorn src.api.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
docker build -t sas-api .
docker run -p 8000:8000 --env-file .env sas-api
```

## 📝 Exemplos de Uso

### Integração com SAS
```python
import requests

# Configurar base URL
BASE_URL = "http://localhost:8000"

# Autorizar SAS
def authorize_sas(sas_address):
    response = requests.post(f"{BASE_URL}/sas/authorize", json={
        "sas_address": sas_address
    })
    return response.json()

# Registrar CBSD
def register_cbsd(cbsd_data):
    response = requests.post(f"{BASE_URL}/cbsd/register", json=cbsd_data)
    return response.json()

# Verificar status
def get_cbsd_info(cbsd_id):
    response = requests.get(f"{BASE_URL}/cbsd/{cbsd_id}")
    return response.json()

## 📦 Exemplos de Uso com curl

### Health Check
```bash
curl http://localhost:8000/health
```

### Autorizar SAS
```bash
curl -X POST http://localhost:8000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
  }'
```

### Revogar SAS
```bash
curl -X POST http://localhost:8000/sas/revoke \
  -H "Content-Type: application/json" \
  -d '{
    "sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
  }'
```

### Verificar autorização SAS
```bash
curl http://localhost:8000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized
```

### Registrar CBSD
```bash
curl -X POST http://localhost:8000/cbsd/register \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "grant_amount": 100000000000000000000,
    "frequency_hz": 3550000000,
    "bandwidth_hz": 10000000,
    "expiry_timestamp": 1750726000
  }'
```

### Obter informações do CBSD
```bash
curl http://localhost:8000/cbsd/1
```

### Listar todos os CBSDs
```bash
curl http://localhost:8000/cbsd
```

### Atualizar grant amount
```bash
curl -X PUT http://localhost:8000/cbsd/grant-amount \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "new_grant_amount": 150000000000000000000
  }'
```

### Atualizar status do CBSD
```bash
curl -X PUT http://localhost:8000/cbsd/status \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "new_status": "active"
  }'
```

### Atualizar detalhes do grant
```bash
curl -X PUT http://localhost:8000/cbsd/grant-details \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "frequency_hz": 3650000000,
    "bandwidth_hz": 20000000,
    "expiry_timestamp": 1750728000
  }'
```

### Obter eventos recentes
```bash
curl http://localhost:8000/events/recent
```

## 🔒 Segurança

- Todas as transações são assinadas com a chave privada configurada
- Validação de dados com Pydantic
- Logs de auditoria de todas as operações
- CORS configurado para desenvolvimento

## 📞 Suporte

Para suporte técnico:
- Verificar logs da API
- Testar conectividade com blockchain
- Verificar configurações no arquivo `.env` 

## Preparar ABI do Contrato
Após o deploy do contrato, copie o arquivo ABI gerado pelo Hardhat para o local esperado pelo middleware:

```bash
mkdir -p src/blockchain/abi
cp ../artifacts/contracts/SASSharedRegistry.sol/SASSharedRegistry.json src/blockchain/abi/SASSharedRegistry.json
```

Se não fizer isso, a API não irá iniciar corretamente 

## Observação

- Todos os endpoints antigos (/sas/authorize, /cbsd/register, etc.) foram removidos. Use apenas os endpoints documentados acima. 