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

### Opção 1: Hardhat Node Local (Desenvolvimento)

#### 1. Instalar Dependências
```bash
npm install
```

#### 2. Testar Contrato
```bash
npx hardhat test
```

#### 3. Iniciar Blockchain
```bash
npx hardhat node
```

#### 4. Deploy do Contrato
```bash
npx hardhat run scripts/deploy-sas-shared-registry.js --network localhost
```

### Opção 2: Quorum Dev Quickstart (Recomendado para Produção)

O [Quorum Dev Quickstart](https://docs.goquorum.consensys.io/tutorials/quorum-dev-quickstart/using-the-quickstart) oferece uma rede blockchain completa com múltiplos nós validadores, ideal para testes e desenvolvimento.

#### 1. Gerar Rede Quorum
```bash
npx quorum-dev-quickstart
```
Siga as instruções:
- Escolha **Hyperledger Besu** como cliente
- Responda **N** para transações privadas
- Escolha **Loki** para logging
- Use o diretório padrão `./quorum-test-network`

#### 2. Iniciar Rede
```bash
cd quorum-test-network
./run.sh
```

#### 3. Verificar Conectividade
```bash
# Verificar versão do cliente
curl -X POST --data '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}' -H 'Content-Type: application/json' http://localhost:8545

# Verificar número de peers
curl -X POST --data '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":1}' -H 'Content-Type: application/json' http://localhost:8545

# Verificar número do bloco
curl -X POST --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' -H 'Content-Type: application/json' http://localhost:8545
```

#### 4. Deploy do Contrato na Rede Quorum
```bash
cd smart_contracts
npm install --legacy-peer-deps
npx hardhat compile
node scripts/deploy-sas-shared-registry-quorum.js
```

**Configurações da Rede Quorum:**
- **RPC URL:** `http://127.0.0.1:8545`
- **Chain ID:** `1337`
- **Contrato Deployado:** `0xBca0fDc68d9b21b5bfB16D784389807017B2bbbc`
- **Chave Privada Owner:** `0x60bbe10a196a4e71451c0f6e9ec9beab454c2a5ac0542aa5b8b733ff5719fec3`

#### 5. Endpoints da Rede Quorum
- **JSON-RPC HTTP:** http://localhost:8545
- **JSON-RPC WebSocket:** ws://localhost:8546
- **Block Explorer:** http://localhost:25000/explorer/nodes
- **Prometheus:** http://localhost:9090/graph
- **Grafana:** http://localhost:3000/d/XE4V0WGZz/besu-overview

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

**Para Rede Quorum Dev Quickstart, configure:**
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0xBca0fDc68d9b21b5bfB16D784389807017B2bbbc
OWNER_PRIVATE_KEY=0x60bbe10a196a4e71451c0f6e9ec9beab454c2a5ac0542aa5b8b733ff5719fec3
CHAIN_ID=1337
```

### 7. Iniciar API
```bash
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
│   ├── deploy-sas-shared-registry.js           # Deploy Hardhat
│   └── deploy-sas-shared-registry-quorum.js    # Deploy Quorum
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

### Endereços de Teste (Quorum Dev Quickstart)
- **Contrato SASSharedRegistry:** `0xBca0fDc68d9b21b5bfB16D784389807017B2bbbc`
- **Owner:** `0xC9C913c8c3C1Cd416d80A0abF475db2062F161f6`
- **RPC Node:** `http://127.0.0.1:8545`

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

### Problemas Comuns com Quorum Dev Quickstart

#### Rede não inicia
```bash
# Parar e remover containers
cd quorum-test-network
./remove.sh

# Reiniciar
./run.sh
```

#### Contrato não faz deploy
- Verifique se a rede está sincronizada (blocos > 0)
- Confirme que a conta tem saldo suficiente
- Use o script `deploy-sas-shared-registry-quorum.js` específico para Quorum

#### Middleware não conecta
- Verifique se o RPC_URL está correto
- Confirme se o CONTRACT_ADDRESS é o correto do deploy
- Teste a conectividade RPC primeiro

## Middleware

> **Nota:** O middleware Python com API REST está disponível na pasta `middleware/` e será documentado separadamente.

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
