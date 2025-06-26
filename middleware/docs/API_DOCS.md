# SAS Shared Registry API Documentation

API REST para comunicação SAS-SAS via blockchain, permitindo que sistemas SAS se comuniquem usando requisições HTTP padrão.

## 🚀 Status: 100% Funcional

✅ **API REST funcionando na porta 9000**  
✅ **Contrato SAS-SAS simplificado**  
✅ **38 testes passando**  
✅ **Integração blockchain local**  
✅ **Eventos funcionando**  

## Iniciar a API

```bash
cd middleware
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 run.py
```

A API estará disponível em: **http://localhost:9000**

---

## Fluxo Completo SAS-SAS

1. **Health Check** → Verificar se API está funcionando
2. **Autorizar SAS** → Dar permissão para um SAS
3. **Registration** → Registrar CBSD via SAS-SAS
4. **Grant** → Solicitar espectro via SAS-SAS
5. **Heartbeat** → Manter grant ativo via SAS-SAS
6. **Events** → Verificar eventos na blockchain

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
  "latest_block": 92,
  "contract_address": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6",
  "owner": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
}
```

### 2. Estatísticas
```bash
GET /stats
```
**Resposta:**
```json
{
  "owner": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
  "contract_address": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6",
  "latest_block": 92,
  "version": "3.0.0 (SAS-SAS)"
}
```

### 3. Autorizar SAS
```bash
POST /sas/authorize
```
**Body:**
```json
{
  "sas_address": "0x1234567890123456789012345678901234567890"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "SAS 0x1234567890123456789012345678901234567890 autorizado",
  "transaction_hash": "0x...",
  "block_number": 93
}
```

### 4. Verificar Autorização SAS
```bash
GET /sas/{sas_address}/authorized
```
**Resposta:**
```json
{
  "sas_address": "0x1234567890123456789012345678901234567890",
  "authorized": true
}
```

### 5. Revogar SAS
```bash
POST /sas/revoke
```
**Body:**
```json
{
  "sas_address": "0x1234567890123456789012345678901234567890"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "SAS 0x1234567890123456789012345678901234567890 revogado",
  "transaction_hash": "0x...",
  "block_number": 94
}
```

### 6. Registration (SAS-SAS)
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
  "latitude": 375000000,
  "longitude": 1224000000,
  "height": 30,
  "heightType": "AGL",
  "indoorDeployment": false,
  "antennaGain": 15,
  "antennaBeamwidth": 360,
  "antennaAzimuth": 0,
  "groupingParam": "",
  "cbsdAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "CBSD TEST-FCC-ID/TEST-CBSD-SERIAL registrado via SAS-SAS",
  "transaction_hash": "0x...",
  "block_number": 95
}
```

### 7. Grant (SAS-SAS)
```bash
POST /v1.3/grant
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "channelType": "GAA",
  "maxEirp": 47,
  "lowFrequency": 3550000000,
  "highFrequency": 3700000000,
  "requestedMaxEirp": 47,
  "requestedLowFrequency": 3550000000,
  "requestedHighFrequency": 3700000000,
  "grantExpireTime": 1750726000
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "Grant solicitado para TEST-FCC-ID/TEST-CBSD-SERIAL via SAS-SAS",
  "transaction_hash": "0x...",
  "block_number": 96
}
```

### 8. Heartbeat (SAS-SAS)
```bash
POST /v1.3/heartbeat
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "grantId": "grant_001",
  "transmitExpireTime": 1750726000
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "Heartbeat executado para TEST-FCC-ID/TEST-CBSD-SERIAL via SAS-SAS",
  "transaction_hash": "0x...",
  "block_number": 97
}
```

### 9. Relinquishment (SAS-SAS)
```bash
POST /v1.3/relinquishment
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL",
  "grantId": "grant_001"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "Relinquishment executado para TEST-FCC-ID/TEST-CBSD-SERIAL via SAS-SAS",
  "transaction_hash": "0x...",
  "block_number": 98
}
```

### 10. Deregistration (SAS-SAS)
```bash
POST /v1.3/deregistration
```
**Body:**
```json
{
  "fccId": "TEST-FCC-ID",
  "cbsdSerialNumber": "TEST-CBSD-SERIAL"
}
```
**Resposta:**
```json
{
  "success": true,
  "message": "CBSD TEST-FCC-ID/TEST-CBSD-SERIAL removido via SAS-SAS",
  "transaction_hash": "0x...",
  "block_number": 99
}
```

### 11. Eventos Recentes
```bash
GET /events/recent
```
**Resposta:**
```json
{
  "events": [
    {
      "event": "Registration",
      "block_number": 95,
      "transaction_hash": "0x...",
      "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      "payload": "{\"fccId\":\"TEST-FCC-ID\",\"userId\":\"TEST-USER-ID\",...}",
      "timestamp": 1703123456
    },
    {
      "event": "Grant",
      "block_number": 96,
      "transaction_hash": "0x...",
      "from": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
      "payload": "{\"fccId\":\"TEST-FCC-ID\",\"cbsdSerialNumber\":\"TEST-CBSD-SERIAL\",...}",
      "timestamp": 1703123457
    }
  ],
  "total": 2
}
```

---

## Modelos de Dados

### RegistrationRequest
```json
{
  "fccId": "string",
  "userId": "string",
  "cbsdSerialNumber": "string",
  "callSign": "string",
  "cbsdCategory": "string",
  "airInterface": "string",
  "measCapability": ["string"],
  "eirpCapability": "integer",
  "latitude": "integer",
  "longitude": "integer",
  "height": "integer",
  "heightType": "string",
  "indoorDeployment": "boolean",
  "antennaGain": "integer",
  "antennaBeamwidth": "integer",
  "antennaAzimuth": "integer",
  "groupingParam": "string",
  "cbsdAddress": "string"
}
```

### GrantRequest
```json
{
  "fccId": "string",
  "cbsdSerialNumber": "string",
  "channelType": "string",
  "maxEirp": "integer",
  "lowFrequency": "integer",
  "highFrequency": "integer",
  "requestedMaxEirp": "integer",
  "requestedLowFrequency": "integer",
  "requestedHighFrequency": "integer",
  "grantExpireTime": "integer"
}
```

### HeartbeatRequest
```json
{
  "fccId": "string",
  "cbsdSerialNumber": "string",
  "grantId": "string",
  "transmitExpireTime": "integer"
}
```

### RelinquishmentRequest
```json
{
  "fccId": "string",
  "cbsdSerialNumber": "string",
  "grantId": "string"
}
```

### DeregistrationRequest
```json
{
  "fccId": "string",
  "cbsdSerialNumber": "string"
}
```

### SASAuthorization
```json
{
  "sas_address": "string"
}
```

---

## Eventos do Blockchain

### Eventos SAS-SAS
- **Registration**: Emitido quando um CBSD é registrado
- **Grant**: Emitido quando um grant é solicitado
- **Heartbeat**: Emitido quando um heartbeat é enviado
- **Relinquishment**: Emitido quando um grant é liberado
- **Deregistration**: Emitido quando um CBSD é removido

### Eventos de Autorização
- **SASAuthorized**: Emitido quando um SAS é autorizado
- **SASRevoked**: Emitido quando um SAS é revogado

---

## Códigos de Erro

### 400 - Bad Request
- Dados inválidos no payload
- SAS não autorizado
- Erro na transação blockchain

### 500 - Internal Server Error
- Erro de conexão com blockchain
- Erro interno da aplicação

---

## Exemplos de Uso

### Script de Teste Básico
```bash
#!/bin/bash

# Health check
echo "=== Health Check ==="
curl -s http://localhost:9000/health | jq

# Stats
echo -e "\n=== Stats ==="
curl -s http://localhost:9000/stats | jq

# Authorize SAS
echo -e "\n=== Authorize SAS ==="
curl -s -X POST http://localhost:9000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x1234567890123456789012345678901234567890"}' | jq

# Registration
echo -e "\n=== Registration ==="
curl -s -X POST http://localhost:9000/v1.3/registration \
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
    "latitude": 375000000,
    "longitude": 1224000000,
    "height": 30,
    "heightType": "AGL",
    "indoorDeployment": false,
    "antennaGain": 15,
    "antennaBeamwidth": 360,
    "antennaAzimuth": 0,
    "groupingParam": "",
    "cbsdAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
  }' | jq

# Events
echo -e "\n=== Recent Events ==="
curl -s http://localhost:9000/events/recent | jq
```

---

## Configuração

### Variáveis de Ambiente
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CHAIN_ID=31337
GAS_LIMIT=3000000
POLLING_INTERVAL=2
LOG_LEVEL=INFO
```

---

## Testes

### Executar Testes
```bash
# Todos os testes
python -m pytest tests/ -v

# Testes específicos
python -m pytest tests/test_api_endpoints.py -v
python -m pytest tests/test_events.py -v
python -m pytest tests/test_middleware.py -v
```

### Scripts de Teste
```bash
# Teste básico
./scripts/test_api.sh

# Teste completo SAS-SAS
./scripts/test_sas_sas.sh
```

---

## Troubleshooting

### API não responde
```bash
# Verificar se está rodando
curl http://localhost:9000/health

# Verificar logs
tail -f logs/app.log
```

### Erro de blockchain
```bash
# Verificar conexão
curl http://localhost:9000/health | jq '.blockchain_connected'

# Verificar contrato
curl http://localhost:9000/stats | jq '.contract_address'
```

### Erro de autorização
```bash
# Verificar se SAS está autorizado
curl http://localhost:9000/sas/{sas_address}/authorized
``` 