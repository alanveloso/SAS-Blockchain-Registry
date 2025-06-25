# SAS Blockchain Registry

Sistema de registro descentralizado baseado em blockchain para comunicação SAS-SAS (Spectrum Access System). O projeto implementa um contrato inteligente que serve como repositório descentralizado de dados para substituir APIs REST tradicionais na comunicação entre sistemas SAS.

O sistema é composto por um smart contract Solidity que garante transparência e imutabilidade das operações SAS-SAS, e um middleware Python que fornece uma API REST para integração com sistemas SAS existentes.

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
                              │                  │  (SAS-SAS)      │
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
3. **EVM Blockchain** ↔ **Smart Contract**: Execução de transações SAS-SAS
4. **Python API** ↔ **Local Cache**: Armazenamento de estado

## Funcionalidades do Smart Contract (SAS-SAS)

### Interface SAS-SAS
O contrato implementa a interface padrão SAS-SAS com as seguintes operações:

- **Registration**: Registro de dispositivos CBSD
- **Grant**: Criação de grants de espectro
- **Heartbeat**: Manutenção de grants ativos
- **Relinquishment**: Liberação de grants
- **Deregistration**: Remoção de dispositivos

### Gestão de Autorização
- **Autorizar SAS**: Permitir que um endereço execute operações SAS-SAS
- **Verificar autorização**: Consultar se um SAS está autorizado
- **Revogar SAS**: Remover autorização de um SAS

### Eventos
Cada operação SAS-SAS emite eventos com payloads JSON que podem ser consumidos por outros sistemas SAS para sincronização.

## Setup do Smart Contract

### Opção 1: Hardhat Node Local (Desenvolvimento)

#### 1. Instalar Dependências
```bash
npm install
```

#### 2. Compilar e Testar Contrato
```bash
npx hardhat compile
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

#### 5. Teste de Integração SAS-SAS
```bash
node scripts/integration-test-sas-simplified.js
```

Esse teste cobre:
- Autorização e revogação de SAS
- Todas as operações SAS-SAS (registration, grant, heartbeat, relinquishment, deregistration)
- Verificação de acesso negado para SAS não autorizado
- Emissão de eventos

### Opção 2: Deploy em Qualquer Rede Besu (Produção/Teste)

Você pode usar qualquer rede compatível com Besu (ex: Hyperledger Besu local, testnet, mainnet privada, etc). Após iniciar sua rede Besu, siga os passos abaixo:

#### 1. Configure o ambiente para apontar para o RPC da sua rede Besu

```env
RPC_URL=http://127.0.0.1:8545 # ou o endpoint da sua rede
CHAIN_ID=<chain_id_da_rede>
OWNER_PRIVATE_KEY=<chave_privada_do_owner>
```

#### 2. Compile e faça o deploy do contrato

```bash
npx hardhat compile
npx hardhat run scripts/deploy-sas-shared-registry.js --network <nome_da_rede_configurada_no_hardhat>
```

#### 3. Copie o endereço do contrato e atualize o .env do middleware

#### 4. Garanta que o ABI do contrato esteja disponível para o middleware

---

## Verificação de Conectividade com a Rede

Antes de prosseguir, verifique se sua rede Besu está acessível e funcional:

**Verificar versão do cliente:**
```bash
curl -X POST \
  --data '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":1}' \
  -H 'Content-Type: application/json' \
  http://localhost:8545
```

**Verificar número de peers:**
```bash
curl -X POST \
  --data '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":1}' \
  -H 'Content-Type: application/json' \
  http://localhost:8545
```

**Verificar número do bloco:**
```bash
curl -X POST \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  -H 'Content-Type: application/json' \
  http://localhost:8545
```

---

## Teste direto do contrato via cURL

Você pode testar a comunicação com o contrato usando cURL e o método `eth_call` da JSON-RPC. Por exemplo, para consultar o owner do contrato:

**Consultar owner do contrato:**

1. Descubra o endereço do contrato (ex: `0x5FbDB2315678afecb367f032d93F642f64180aa3`).
2. Descubra o selector da função (ex: `owner()` → `0x8da5cb5b`).

```bash
curl -X POST \
  --data '{
    "jsonrpc":"2.0",
    "method":"eth_call",
    "params":[{
      "to": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
      "data": "0x8da5cb5b"
    }, "latest"],
    "id":1
  }' \
  -H 'Content-Type: application/json' \
  http://localhost:8545
```

O resultado será o endereço do owner em hexadecimal.

Você pode adaptar o `data` para outros métodos públicos do contrato, consultando o ABI e calculando o selector correspondente.

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

**Ajuste as variáveis principais no `.env` conforme o deploy:**
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CHAIN_ID=31337
```

Garanta que o ABI do contrato esteja em `middleware/src/blockchain/abi/SASSharedRegistry.json`.

### 7. Iniciar API
```bash
python3 run.py
```

### 8. Testar Middleware
```bash
./scripts/test_api.sh
./scripts/test_blockchain.sh
```

## Testes de Integração do Contrato

Após o deploy do contrato, execute o teste de integração SAS-SAS:

```bash
node scripts/integration-test-sas-simplified.js
```

Esse teste cobre:
- Autorização e revogação de SAS
- Todas as operações SAS-SAS (registration, grant, heartbeat, relinquishment, deregistration)
- Verificação de acesso negado para SAS não autorizado
- Emissão de eventos com payloads JSON

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

### Operação SAS-SAS (Registration)
```bash
curl -X POST http://localhost:8000/sas/registration \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-001",
    "userId": "TEST-USER-001",
    "cbsdSerialNumber": "TEST-SN-001",
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

### Eventos Recentes
```bash
curl http://localhost:8000/events/recent | jq
```

## Estrutura do Projeto

```
SAS-Blockchain-Registry/
├── contracts/
│   ├── SASSharedRegistry.sol    # Smart contract SAS-SAS
│   └── Lock.sol                 # Contrato de exemplo
├── middleware/                  # API Python (documentação separada)
├── scripts/
│   ├── deploy-sas-shared-registry.js           # Deploy Hardhat
│   └── integration-test-sas-simplified.js      # Teste SAS-SAS
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

### Testes de Integração (SAS-SAS)
```bash
node scripts/integration-test-sas-simplified.js
```

## Configurações

### Endereços de Teste (Hardhat)
- **SAS de Teste:** `0x70997970C51812dc3A010C7d01b50e0d17dc79C8`
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
