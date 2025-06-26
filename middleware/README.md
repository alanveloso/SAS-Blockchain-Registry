# SAS Blockchain Registry Middleware

Middleware Python para interação com o contrato SAS Shared Registry via API REST. Fornece uma interface padronizada para sistemas SAS integrarem com a blockchain de forma transparente e segura.

## 🚀 Status: 100% Funcional

✅ **API REST funcionando na porta 9000**  
✅ **Contrato SAS-SAS simplificado**  
✅ **38 testes passando**  
✅ **Integração blockchain local**  
✅ **Eventos funcionando**  

## Estrutura do Projeto

```
middleware/
├── src/                    # Código fonte principal
│   ├── api/               # API REST FastAPI
│   │   ├── __init__.py
│   │   └── api.py         # Endpoints da API
│   ├── blockchain/        # Interação com blockchain
│   │   ├── __init__.py
│   │   └── blockchain.py  # Cliente Web3
│   ├── handlers/          # Handlers de eventos
│   │   ├── __init__.py
│   │   └── handlers.py    # Processamento de eventos
│   ├── repository/        # Repositório de dados
│   │   ├── __init__.py
│   │   └── repository.py  # Cache local
│   ├── config/            # Configurações
│   │   ├── __init__.py
│   │   ├── config.py      # Configuração antiga
│   │   └── settings.py    # Configuração nova (Pydantic)
│   └── __init__.py
├── tests/                 # Testes (38 testes passando)
│   ├── test_api_endpoints.py
│   ├── test_events.py
│   └── test_middleware.py
├── docs/                  # Documentação
│   └── API_DOCS.md
├── scripts/               # Scripts utilitários
│   ├── test_api.sh        # Teste básico da API
│   └── test_sas_sas.sh    # Teste completo SAS-SAS
├── logs/                  # Logs da aplicação
├── abi/                   # ABI do contrato
├── venv/                  # Ambiente virtual
├── .env                   # Variáveis de ambiente
├── requirements.txt       # Dependências Python
├── run.py                 # Ponto de entrada principal
├── app.py                 # Ponto de entrada alternativo
├── setup.sh               # Script de instalação
└── README.md              # Este arquivo
```

## Setup

### 1. Instalar Dependências
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
cp env.example .env
# Editar .env com suas configurações
```

### 3. Executar a API
```bash
python3 run.py
```

A API estará disponível em: **http://localhost:9000**

### 4. Testar

#### Testes Básicos (API)

**Health Check**
```bash
curl http://localhost:9000/health | jq
```

**Endpoint Raiz**
```bash
curl http://localhost:9000/ | jq
```

**Estatísticas**
```bash
curl http://localhost:9000/stats | jq
```

#### Testes Completos (SAS-SAS)

**Autorizar SAS**
```bash
curl -s -X POST http://localhost:9000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x1234567890123456789012345678901234567890"}' | jq
```

**Registrar CBSD via SAS-SAS**
```bash
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
```

**Solicitar Grant via SAS-SAS**
```bash
curl -s -X POST http://localhost:9000/v1.3/grant \
  -H "Content-Type: application/json" \
  -d '{
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
  }' | jq
```

**Heartbeat via SAS-SAS**
```bash
curl -s -X POST http://localhost:9000/v1.3/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "grantId": "grant_001",
    "transmitExpireTime": 1750726000
  }' | jq
```

**Verificar Eventos**
```bash
curl http://localhost:9000/events/recent | jq
```

## Configuração

### Variáveis de Ambiente (.env)
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CHAIN_ID=31337
GAS_LIMIT=3000000
POLLING_INTERVAL=2
LOG_LEVEL=INFO
```

### Preparar ABI do Contrato
O ABI do contrato já está disponível em `src/blockchain/abi/SASSharedRegistry.json` e foi copiado automaticamente durante o setup.

## Testes Automatizados

### Executar Todos os Testes
```bash
python -m pytest tests/ -v
```

### Executar Testes Específicos
```bash
# Testes de API
python -m pytest tests/test_api_endpoints.py -v

# Testes de Eventos
python -m pytest tests/test_events.py -v

# Testes de Middleware
python -m pytest tests/test_middleware.py -v
```

### Scripts de Teste
```bash
# Teste básico da API
./scripts/test_api.sh

# Teste completo SAS-SAS
./scripts/test_sas_sas.sh
```

## Documentação

- **[API_DOCS.md](docs/API_DOCS.md)** - Documentação técnica da API
- **README.md** - Guia principal do projeto

## Troubleshooting

### Erro de Importação
Se houver problemas com imports:
```bash
# Verificar se está no ambiente virtual
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro de Porta
Se a porta 9000 estiver ocupada:
```bash
fuser -k 9000/tcp
```

### Verificar Status da API
```bash
curl http://localhost:9000/health | jq
```

## Funcionalidades Implementadas

### ✅ Gestão de SAS
- Autorizar SAS
- Verificar autorização
- Revogar SAS

### ✅ Operações SAS-SAS
- Registration
- Grant
- Heartbeat
- Relinquishment
- Deregistration

### ✅ Consultas e Monitoramento
- Ver eventos recentes
- Health check da API
- Status da conexão blockchain
- Estatísticas do contrato

## Contrato SAS-SAS Simplificado

O contrato foi simplificado para focar apenas na interface SAS-SAS:

- **Eventos SAS-SAS**: Registration, Grant, Heartbeat, Relinquishment, Deregistration
- **Autorização SAS**: SASAuthorized, SASRevoked
- **Payload JSON**: Todas as operações usam payload JSON para flexibilidade

## Próximos Passos

1. **Implementar autenticação JWT**
2. **Adicionar rate limiting**
3. **Implementar cache Redis**
4. **Adicionar métricas Prometheus**
5. **Containerização com Docker**
6. **Deploy em rede de teste**

## Fluxo de Registro e Consulta (Exemplo Real)

1. **Health Check** → Verificar se API está funcionando
2. **Autorizar SAS** → Dar permissão para um SAS
3. **Registration** → Registrar CBSD via SAS-SAS
4. **Grant** → Solicitar espectro via SAS-SAS
5. **Heartbeat** → Manter grant ativo via SAS-SAS
6. **Events** → Verificar eventos na blockchain