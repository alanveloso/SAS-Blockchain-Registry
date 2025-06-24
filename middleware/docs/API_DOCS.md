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

## Endpoints

### Health Check
```bash
GET /health
```

**Resposta:**
```json
{
  "status": "healthy",
  "blockchain_connected": true,
  "latest_block": 1938,
  "contract_address": "0x5FbDB2315678afecb367f032d93F642f64180aa3"
}
```

### Autorizar SAS
```bash
POST /sas/authorize
```

**Body:**
```json
{
  "sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "SAS 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 autorizado",
  "transaction_hash": "0x...",
  "block_number": 1939
}
```

### Revogar SAS
```bash
POST /sas/revoke
```

**Body:**
```json
{
  "sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
}
```

### Verificar Autorização SAS
```bash
GET /sas/{sas_address}/authorized
```

**Resposta:**
```json
{
  "sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
  "authorized": true
}
```

### Registrar CBSD
```bash
POST /cbsd/register
```

**Body:**
```json
{
  "cbsd_id": 1,
  "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
  "grant_amount": 100000000000000000000,
  "frequency_hz": 3550000000,
  "bandwidth_hz": 10000000,
  "expiry_timestamp": 1750726000
}
```

### Obter Informações do CBSD
```bash
GET /cbsd/{cbsd_id}
```

**Resposta:**
```json
{
  "cbsd_id": 1,
  "blockchain_data": {
    "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "grant_amount": 100000000000000000000,
    "status": "registered",
    "frequency_hz": 3550000000,
    "bandwidth_hz": 10000000,
    "expiry_timestamp": 1750726000,
    "sas_origin": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
  },
  "local_data": {
    "id": 1,
    "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "grant_amount": 100000000000000000000,
    "status": "registered",
    "frequency_hz": 3550000000,
    "bandwidth_hz": 10000000,
    "expiry_timestamp": 1750726000,
    "block_number": 1939,
    "transaction_hash": "0x..."
  }
}
```

### Atualizar Grant Amount
```bash
PUT /cbsd/grant-amount
```

**Body:**
```json
{
  "cbsd_id": 1,
  "new_grant_amount": 150000000000000000000
}
```

### Atualizar Status
```bash
PUT /cbsd/status
```

**Body:**
```json
{
  "cbsd_id": 1,
  "new_status": "active"
}
```

### Atualizar Detalhes do Grant
```bash
PUT /cbsd/grant-details
```

**Body:**
```json
{
  "cbsd_id": 1,
  "frequency_hz": 3650000000,
  "bandwidth_hz": 20000000,
  "expiry_timestamp": 1750728000
}
```

### Listar Todos os CBSDs
```bash
GET /cbsd
```

**Resposta:**
```json
{
  "total": 1,
  "cbsds": [
    {
      "cbsd_id": 1,
      "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
      "grant_amount": 100000000000000000000,
      "status": "registered",
      "frequency_hz": 3550000000,
      "bandwidth_hz": 10000000,
      "expiry_timestamp": 1750726000,
      "block_number": 1939,
      "transaction_hash": "0x..."
    }
  ]
}
```

### Obter Eventos Recentes
```bash
GET /events/recent
```

**Resposta:**
```json
{
  "total_events": 1,
  "events": [
    {
      "cbsd_id": 1,
      "event_type": "CBSDRegistered",
      "transaction_hash": "0x...",
      "block_number": 1939,
      "timestamp": 1939
    }
  ]
}
```

## 🧪 Testes Automatizados

### Teste Básico (Sem Blockchain)
```bash
./scripts/test_api.sh
```

### Teste Completo (Com Blockchain)
```bash
./scripts/test_blockchain.sh
```

## ⚙️ Configuração

### Variáveis de Ambiente
A API usa as mesmas variáveis do middleware:
- `RPC_URL`: URL do nó Besu
- `CONTRACT_ADDRESS`: Endereço do contrato
- `OWNER_PRIVATE_KEY`: Chave privada do owner
- `CHAIN_ID`: ID da rede

### CORS
A API está configurada para aceitar requisições de qualquer origem (`*`).

## 📊 Códigos de Status HTTP

- `200`: Sucesso
- `400`: Erro de requisição (dados inválidos)
- `404`: Recurso não encontrado
- `500`: Erro interno do servidor

## 🔍 Monitoramento

### Health Check
```bash
curl http://localhost:8000/health
```

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