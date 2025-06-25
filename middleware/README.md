# SAS Blockchain Registry Middleware

Middleware Python para interação com o contrato SAS Shared Registry via API REST. Fornece uma interface padronizada para sistemas SAS integrarem com a blockchain de forma transparente e segura.

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
├── tests/                 # Testes
│   ├── test_events.py
│   └── test_middleware.py
├── docs/                  # Documentação
│   └── API_DOCS.md
├── scripts/               # Scripts utilitários
│   ├── test_api.sh              # Teste básico (sem blockchain)
│   └── test_blockchain.sh       # Teste completo (com blockchain)
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

### 4. Testar

#### Testes Básicos (Sem Blockchain)

**Health Check**
```bash
curl http://localhost:8000/health | jq
```

**Endpoint Raiz**
```bash
curl http://localhost:8000/ | jq
```

#### Testes Completos (Com Blockchain)

**Health Check**
```bash
curl http://localhost:8000/health | jq
```

**Autorizar FCC ID**
```bash
curl -s -X POST http://localhost:8000/v1.3/admin/injectFccId \
  -H "Content-Type: application/json" \
  -d '{"fccId": "TEST-FCC-ID", "maxEirp": 47}' | jq
```

**Autorizar User ID**
```bash
curl -s -X POST http://localhost:8000/v1.3/admin/injectUserId \
  -H "Content-Type: application/json" \
  -d '{"userId": "TEST-USER-ID"}' | jq
```

**Registrar CBSD**
```bash
curl -s -X POST http://localhost:8000/v1.3/registration \
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
  }' | jq
```

**Consultar CBSD**
```bash
curl -s http://localhost:8000/cbsd/TEST-FCC-ID/TEST-CBSD-SERIAL | jq
```

## Configuração

### Variáveis de Ambiente (.env)
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CHAIN_ID=31337
GAS_LIMIT=3000000
POLLING_INTERVAL=2
LOG_LEVEL=INFO
```

### Preparar ABI do Contrato
O ABI do contrato já está disponível em `src/blockchain/abi/SASSharedRegistry.json` e foi copiado automaticamente durante o setup.

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
Se a porta 8000 estiver ocupada:
```bash
fuser -k 8000/tcp
```

## Próximos Passos

1. **Implementar autenticação JWT**
2. **Adicionar rate limiting**
3. **Implementar cache Redis**
4. **Adicionar métricas Prometheus**
5. **Containerização com Docker**
6. **Deploy em rede de teste**

## Funcionalidades

### Gestão de SAS
- Autorizar SAS
- Verificar autorização
- Revogar SAS

### Gestão de CBSD
- Registrar CBSD
- Atualizar grant amount
- Atualizar status
- Atualizar detalhes do grant
- Consultar informações

### Consultas e Monitoramento
- Listar todos os CBSDs
- Ver eventos recentes
- Health check da API
- Status da conexão blockchain

## Fluxo de Registro e Consulta (Exemplo Real)

### 1. Health Check
```bash
curl -s http://localhost:8000/health | jq
```

### 2. Autorizar FCC ID
```bash
curl -s -X POST http://localhost:8000/v1.3/admin/injectFccId \
  -H "Content-Type: application/json" \
  -d '{"fccId": "TEST-FCC-ID", "maxEirp": 47}' | jq
```

### 3. Autorizar User ID
```bash
curl -s -X POST http://localhost:8000/v1.3/admin/injectUserId \
  -H "Content-Type: application/json" \
  -d '{"userId": "TEST-USER-ID"}' | jq
```

### 4. Registrar CBSD
```bash
curl -s -X POST http://localhost:8000/v1.3/registration \
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
  }' | jq
```

### 5. Consultar CBSD
```bash
curl -s http://localhost:8000/cbsd/TEST-FCC-ID/TEST-CBSD-SERIAL | jq
```