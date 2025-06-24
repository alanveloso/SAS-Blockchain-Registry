# SAS Blockchain Registry

Sistema completo de gestão de espectro radioelétrico baseado em blockchain para CBRS (Citizen Broadband Radio Service). O projeto implementa um registro descentralizado que permite a autorização de SAS (Spectrum Access System), registro de CBSD (Citizen Broadband Radio Service Device), gestão de grants de espectro e monitoramento de eventos em tempo real.

O sistema é composto por um smart contract Solidity que garante transparência e imutabilidade das operações, e um middleware Python que fornece uma API REST para integração com sistemas SAS existentes.

## Arquitetura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SAS System    │    │  Python API      │    │  EVM Blockchain │
│                 │◄──►│  (FastAPI)       │◄──►│  (Ethereum/     │
│                 │    │                  │    │   Polygon/      │
│                 │    │                  │    │   Besu/etc.)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                           │
                              │                           ▼
                              │                  ┌─────────────────┐
                              │                  │  Smart Contract │
                              │                  │  SASShared      │
                              │                  │  Registry.sol   │
                              │                  └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Local Cache     │
                       │  (Repository)    │
                       └──────────────────┘
```

**Fluxo de Dados:**
1. **SAS System** ↔ **Python API**: Comunicação via REST
2. **Python API** ↔ **EVM Blockchain**: Interação via Web3
3. **EVM Blockchain** ↔ **Smart Contract**: Execução de transações
4. **Python API** ↔ **Local Cache**: Armazenamento de estado

## Setup do Smart Contract

### 1. Instalar Dependências
```bash
npm install
```

### 2. Testar Contrato
```bash
npx hardhat test
```

### 3. Iniciar Blockchain
```bash
npx hardhat node
```

### 4. Deploy do Contrato
```bash
npx hardhat run scripts/deploy-sas-shared-registry.js --network localhost
```

## Setup do Middleware

### 5. Configurar Ambiente Python
```bash
cd middleware
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 6. Configurar Variáveis de Ambiente
```bash
cp env.example .env
```

### 7. Iniciar API
```bash
source venv/bin/activate
python3 run.py
```

### 8. Testar Middleware
```bash
./scripts/test_api.sh
./scripts/test_blockchain.sh
```

## Testes com cURL

### Health Check
```bash
curl http://localhost:8000/health | jq
```

### Autorizar SAS
```bash
curl -X POST http://localhost:8000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq
```

### Verificar Autorização SAS
```bash
curl http://localhost:8000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized | jq
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
  }' | jq
```

### Consultar CBSD
```bash
curl http://localhost:8000/cbsd/1 | jq
```

### Listar Todos os CBSDs
```bash
curl http://localhost:8000/cbsd | jq
```

### Eventos Recentes
```bash
curl http://localhost:8000/events/recent | jq
```

## Funcionalidades do Smart Contract

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

## Estrutura do Projeto

```
SAS-Blockchain-Registry/
├── contracts/
│   ├── SASSharedRegistry.sol    # Smart contract principal
│   └── Lock.sol                 # Contrato de exemplo
├── middleware/                  # API Python (documentação separada)
├── scripts/
│   └── deploy-sas-shared-registry.js  # Script de deploy
├── test/
│   └── SASSharedRegistry.js     # Testes unitários
├── hardhat.config.js            # Configuração Hardhat
└── README.md                    # Este arquivo
```

## Testes

### Testes Unitários (Smart Contract)
```bash
npx hardhat test
```

## Configurações

### Endereços de Teste (Hardhat)
- **SAS de Teste:** `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
- **CBSD de Teste:** `0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC`
- **Owner:** `0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266`

## Troubleshooting

### Verificar se o nó está rodando
```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  http://127.0.0.1:8545
```

### Verificar chainId
```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  http://127.0.0.1:8545
```

## Middleware

> **Nota:** O middleware Python com API REST está disponível na pasta `middleware/` e será documentado separadamente.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
