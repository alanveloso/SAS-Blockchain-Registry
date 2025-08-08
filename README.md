# SAS Blockchain Registry

Sistema de registro descentralizado baseado em blockchain para comunicação SAS-SAS (Spectrum Access System). O projeto implementa um contrato inteligente robusto, alinhado ao padrão WINNF-TS-0096, que serve como repositório descentralizado de dados para substituir APIs REST tradicionais na comunicação entre sistemas SAS.

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

### Interface SAS-SAS (WINNF-TS-0096)
O contrato implementa a interface robusta SAS-SAS, incluindo:

- **registration**: Registro de dispositivos CBSD (struct RegistrationRequest)
- **grant**: Criação de grants de espectro (struct GrantRequest)
- **relinquishment**: Liberação de grants
- **deregistration**: Remoção de dispositivos
- **authorizeSAS / revokeSAS**: Gestão de autorização de SAS

> **Nota:** Não há mais função heartbeat nem payloads genéricos. Todos os dados são passados via structs tipados (arrays ordenados ao chamar via ethers.js).

### Eventos
Cada operação SAS-SAS emite eventos específicos (ex: `CBSDRegistered`, `GrantCreated`, `GrantTerminated`).

---

## Setup do Smart Contract

### Setup do Smart Contract

#### 1. Instalar Dependências
```bash
npm install
```

#### 2. Compilar
```bash
npx hardhat compile
```

#### 3. Iniciar Blockchain
```bash
npx hardhat node
```

#### 4. Deploy do Contrato

**Nota:** O Hardhat já vem configurado com a rede `localhost` por padrão. Para outras redes (Besu, etc.), configure no `hardhat.config.js` e use `--network <nome_da_rede>`.

```bash
npx hardhat console --network localhost
```

No console:
```javascript
const SASSharedRegistry = await ethers.getContractFactory("SASSharedRegistry");
const sasSharedRegistry = await SASSharedRegistry.deploy();
await sasSharedRegistry.waitForDeployment();
const address = await sasSharedRegistry.getAddress();
const [deployer] = await ethers.getSigners();
console.log("Contrato:", address);
console.log("Conta:", deployer.address);

.exit
```

#### 5. Configurar .env
Copie as informações do console para o arquivo `.env`:
```bash
cd gateway
cp env.example .env
```

Editar o `.env` com as informações do deploy:
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=<endereço_do_contrato>
OWNER_PRIVATE_KEY=<chave_privada_do_hardhat>
CHAIN_ID=31337
```

**Nota:** A chave privada padrão do Hardhat é: `0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80`

#### 6. Executar API
```bash
cd gateway
python app.py
```


## Exemplo de Uso

```js
const registrationArgs = [
  "FCC123", "USR1", "SN123", "CALL", "A", "E-UTRA", ["RECEIVED_POWER_WITHOUT_GRANT"],
  30, 12345, 67890, 10, "AGL", false, 5, 60, 90, "group1", "0x..."
];
await contract.registration(registrationArgs);
```

---

## Testes

```bash
npx hardhat test
```

---

## Scripts

```bash
# Deploy manual
npx hardhat console --network localhost

# Deploy automatizado
npx hardhat run scripts/deploy-sas-shared-registry.js --network localhost

# Análise de performance
python3 scripts/analyze_results.py
```



## Configuração do .env

Após o deploy, copie as informações do console para o arquivo `.env`:

```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=<endereço_do_contrato>
OWNER_PRIVATE_KEY=<chave_privada>
CHAIN_ID=<chain_id>
```
- **Testes unitários:**
  ```bash
  npx hardhat test
  ```

---

## Variáveis de Ambiente (.env)
```env
RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
OWNER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CHAIN_ID=31337
```

Garanta que o ABI do contrato esteja em `middleware/src/blockchain/abi/SASSharedRegistry.json`.

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

## Testes do Contrato

Após o deploy do contrato, execute o teste de integração SAS-SAS:

```bash
npx hardhat test
```

Os testes unitários cobrem:
- Autorização e revogação de SAS
- Todas as operações SAS-SAS (registration, grant, relinquishment, deregistration)
- Verificação de acesso negado para SAS não autorizado
- Emissão de eventos específicos

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
│   └── (testes unitários via npx hardhat test)
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

### Testes de API
```bash
cd gateway && python -m pytest tests/
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

