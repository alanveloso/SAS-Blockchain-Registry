# SAS Blockchain Registry Gateway

Gateway Python para integração REST com o contrato SASSharedRegistry (Solidity), alinhado ao padrão WINNF-TS-0096. Suporte completo a registro, grant, relinquishment, deregistration e autorização SAS, com eventos robustos e interface estruturada.

## 🚀 Status: 100% Funcional

✅ **API REST funcionando na porta 9000**  
✅ **Contrato SAS-SAS robusto (WINNF-TS-0096)**  
✅ **Testes automatizados passando**  
✅ **Integração blockchain local**  
✅ **Eventos funcionando**  

## Estrutura do Projeto

```
gateway/
├── src/                    # Código fonte principal
│   ├── api/               # API REST FastAPI
│   │   └── api.py         # Endpoints da API
│   ├── blockchain/        # Interação com blockchain
│   │   └── blockchain.py  # Cliente Web3
│   ├── handlers/          # Handlers de eventos
│   │   └── handlers.py    # Processamento de eventos
│   ├── repository/        # Repositório de dados
│   │   └── repository.py  # Cache local
│   ├── config/            # Configurações
│   │   └── settings.py    # Configuração (Pydantic)
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
├── scripts/               # Scripts utilitários
├── logs/                  # Logs da aplicação
├── abi/                   # ABI do contrato
├── venv/                  # Ambiente virtual
├── .env                   # Variáveis de ambiente
├── requirements.txt       # Dependências Python
├── run.py                 # Ponto de entrada principal
└── README.md              # Este arquivo
```

## Principais Endpoints

- `/v1.3/registration` — Registra CBSD (payload: struct, sem payload genérico)
- `/v1.3/grant` — Solicita grant (payload: struct)
- `/v1.3/relinquishment` — Libera grant (payload: struct, grantId real)
- `/v1.3/deregistration` — Remove CBSD (payload: struct)
- `/sas/authorize` e `/sas/revoke` — Gerencia SAS autorizados
- `/events/recent` — Lista eventos recentes (nomes: `CBSDRegistered`, `GrantCreated`, `GrantTerminated`, `SASAuthorized`, `SASRevoked`)

## Exemplo de Evento Retornado
```json
{
  "event": "GrantCreated",
  "block_number": 123,
  "transaction_hash": "0x...",
  "sasOrigin": "0x...",
  "fccId": "TEST-FCC-ID",
  "serialNumber": "TEST-CBSD-SERIAL",
  "grantId": "grant_TEST-FCC-IDTEST-CBSD-SERIAL0",
  "timestamp": 123
}
```
> Todos os campos são serializáveis em JSON. Não há mais campo `payload` genérico.

## Fluxo de Uso
1. **Autorize SAS** (se necessário)
2. **Registre CBSD**
3. **Solicite Grant**
4. **Libere Grant** (usando o `grantId` retornado no evento `GrantCreated`)
5. **Deregistre CBSD** (opcional)
6. **Consulte eventos para auditoria**

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
```bash
curl http://localhost:9000/health | jq
curl http://localhost:9000/ | jq
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
    "airInterface": "E-UTRA",
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

**Relinquishment via SAS-SAS**
```bash
# Use o grantId retornado no evento GrantCreated
curl -s -X POST http://localhost:9000/v1.3/relinquishment \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL",
    "grantId": "grant_TEST-FCC-IDTEST-CBSD-SERIAL0"
  }' | jq
```

**Deregistration via SAS-SAS**
```bash
curl -s -X POST http://localhost:9000/v1.3/deregistration \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-ID",
    "cbsdSerialNumber": "TEST-CBSD-SERIAL"
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
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
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
source venv/bin/activate
PYTHONPATH=src pytest tests -v
```

## Dicas e Observações
- O contrato Solidity **não emite evento para deregistration** (isso é esperado pelo padrão).
- Todos os eventos relevantes são: `CBSDRegistered`, `GrantCreated`, `GrantTerminated`, `SASAuthorized`, `SASRevoked`.
- O campo `grantId` deve ser obtido do evento `GrantCreated` para operações de relinquishment.
- O gateway não usa mais heartbeat nem payloads genéricos.

## Referências
- WINNF-TS-0096: [Especificação oficial](https://winnforum.org/standards)
- Solidity Contract: `contracts/SASSharedRegistry.sol`
- ABI: `gateway/src/blockchain/abi/SASSharedRegistry.json`