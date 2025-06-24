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

**Autorizar SAS**
```bash
curl -X POST http://localhost:8000/sas/authorize -H "Content-Type: application/json" -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq
```

**Registrar CBSD**
```bash
curl -X POST http://localhost:8000/cbsd/register -H "Content-Type: application/json" -d '{"cbsd_id": 1, "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC", "grant_amount": 100000000000000000000, "frequency_hz": 3550000000, "bandwidth_hz": 10000000, "expiry_timestamp": 1750726000}' | jq
```

**Consultar CBSD**
```bash
curl http://localhost:8000/cbsd/1 | jq
```

**Listar Todos os CBSDs**
```bash
curl http://localhost:8000/cbsd | jq
```

**Verificar Autorização SAS**
```bash
curl http://localhost:8000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized | jq
```

**Atualizar Grant Amount**
```bash
curl -X PUT http://localhost:8000/cbsd/grant-amount -H "Content-Type: application/json" -d '{"cbsd_id": 1, "new_grant_amount": 150000000000000000000}' | jq
```

**Atualizar Status do CBSD**
```bash
curl -X PUT http://localhost:8000/cbsd/status -H "Content-Type: application/json" -d '{"cbsd_id": 1, "new_status": "active"}' | jq
```

**Atualizar Detalhes do Grant**
```bash
curl -X PUT http://localhost:8000/cbsd/grant-details -H "Content-Type: application/json" -d '{"cbsd_id": 1, "frequency_hz": 3650000000, "bandwidth_hz": 20000000, "expiry_timestamp": 1750728000}' | jq
```

**Revogar SAS**
```bash
curl -X POST http://localhost:8000/sas/revoke -H "Content-Type: application/json" -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq
```

**Eventos Recentes**
```bash
curl http://localhost:8000/events/recent | jq
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