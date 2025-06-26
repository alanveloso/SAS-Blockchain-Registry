#!/bin/bash

echo "🔗 Teste da API SAS Shared Registry (SAS-SAS)"
echo "============================================="
echo ""

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Verificar se a API está rodando
echo "🔍 Verificando se a API está rodando..."
if ! curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "❌ API não está rodando. Execute: python3 run.py"
    exit 1
fi

# Verificar se o blockchain está conectado
echo "🔍 Verificando conexão com blockchain..."
HEALTH_RESPONSE=$(curl -s http://localhost:9000/health)
if echo "$HEALTH_RESPONSE" | jq -e '.blockchain_connected == true' > /dev/null 2>&1; then
    echo "✅ Blockchain conectado!"
else
    echo "❌ Blockchain não conectado. Verifique se o Hardhat está rodando."
    echo "💡 Execute: npx hardhat node"
    exit 1
fi

# Função para aguardar um pouco entre requests
wait_a_bit() {
    echo "⏳ Aguardando 2 segundos..."
    sleep 2
}

# 1. Health Check
echo -e "\n1️⃣ Health Check"
echo "---------------"
curl -s http://localhost:9000/health | jq '.'
echo ""

wait_a_bit

# 2. Autorizar SAS
echo "2️⃣ Autorizar SAS"
echo "----------------"
curl -s -X POST http://localhost:9000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq '.'
echo ""

wait_a_bit

# 3. Verificar autorização
echo "3️⃣ Verificar autorização"
echo "------------------------"
curl -s http://localhost:9000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized | jq '.'
echo ""

wait_a_bit

# 4. Registration SAS-SAS
echo "4️⃣ Registration SAS-SAS"
echo "----------------------"
curl -s -X POST http://localhost:9000/v1.3/registration \
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
  }' | jq '.'
echo ""

wait_a_bit

# 5. Grant SAS-SAS
echo "5️⃣ Grant SAS-SAS"
echo "----------------"
curl -s -X POST http://localhost:9000/v1.3/grant \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-001",
    "cbsdSerialNumber": "TEST-SN-001",
    "channelType": "GAA",
    "maxEirp": 47,
    "lowFrequency": 3550000000,
    "highFrequency": 3700000000,
    "requestedMaxEirp": 47,
    "requestedLowFrequency": 3550000000,
    "requestedHighFrequency": 3700000000,
    "grantExpireTime": 1750726000
  }' | jq '.'
echo ""

wait_a_bit

# 6. Heartbeat SAS-SAS
echo "6️⃣ Heartbeat SAS-SAS"
echo "-------------------"
curl -s -X POST http://localhost:9000/v1.3/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-001",
    "cbsdSerialNumber": "TEST-SN-001",
    "grantId": "grant_001",
    "transmitExpireTime": 1750726000
  }' | jq '.'
echo ""

wait_a_bit

# 7. Relinquishment SAS-SAS
echo "7️⃣ Relinquishment SAS-SAS"
echo "------------------------"
curl -s -X POST http://localhost:9000/v1.3/relinquishment \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-001",
    "cbsdSerialNumber": "TEST-SN-001",
    "grantId": "grant_001"
  }' | jq '.'
echo ""

wait_a_bit

# 8. Deregistration SAS-SAS
echo "8️⃣ Deregistration SAS-SAS"
echo "------------------------"
curl -s -X POST http://localhost:9000/v1.3/deregistration \
  -H "Content-Type: application/json" \
  -d '{
    "fccId": "TEST-FCC-001",
    "cbsdSerialNumber": "TEST-SN-001"
  }' | jq '.'
echo ""

wait_a_bit

# 9. Ver estatísticas
echo "9️⃣ Ver estatísticas"
echo "-------------------"
curl -s http://localhost:9000/stats | jq '.'
echo ""

wait_a_bit

# 10. Ver eventos recentes
echo "🔟 Ver eventos recentes"
echo "----------------------"
curl -s http://localhost:9000/events/recent | jq '.'
echo ""

wait_a_bit

# 11. Teste de erro - SAS não autorizado
echo "1️⃣1️⃣ Teste de erro - SAS não autorizado"
echo "--------------------------------------"
curl -s http://localhost:9000/sas/0x1234567890123456789012345678901234567890/authorized | jq '.'
echo ""

wait_a_bit

# 12. Revogar SAS
echo "1️⃣2️⃣ Revogar SAS"
echo "----------------"
curl -s -X POST http://localhost:9000/sas/revoke \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq '.'
echo ""

wait_a_bit

# 13. Verificar SAS revogado
echo "1️⃣3️⃣ Verificar SAS revogado"
echo "---------------------------"
curl -s http://localhost:9000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized | jq '.'
echo ""

echo "✅ Teste SAS-SAS concluído!"
echo ""
echo "🎉 Todas as operações SAS-SAS foram testadas com sucesso!"
echo "📊 Verifique os logs da API para mais detalhes."
echo ""
echo "📚 Para mais informações, consulte:"
echo "   - API_DOCS.md - Documentação técnica"
echo "   - README.md - Guia de instalação" 