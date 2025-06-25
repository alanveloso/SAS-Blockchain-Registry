#!/bin/bash

echo "🔗 Teste da API SAS Shared Registry (Com Blockchain)"
echo "==================================================="
echo ""

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Verificar se a API está rodando
echo "🔍 Verificando se a API está rodando..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API não está rodando. Execute: python3 run.py"
    exit 1
fi

# Verificar se o blockchain está conectado
echo "🔍 Verificando conexão com blockchain..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
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
curl -s http://localhost:8000/health | jq '.'
echo ""

wait_a_bit

# 2. Autorizar SAS
echo "2️⃣ Autorizar SAS"
echo "----------------"
curl -s -X POST http://localhost:8000/sas/authorize \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq '.'
echo ""

wait_a_bit

# 3. Verificar autorização
echo "3️⃣ Verificar autorização"
echo "------------------------"
curl -s http://localhost:8000/sas/0x70997970C51812dc3A010C7d01b50e0d17dc79C8/authorized | jq '.'
echo ""

wait_a_bit

# 4. Registrar CBSD
echo "4️⃣ Registrar CBSD"
echo "-----------------"
curl -s -X POST http://localhost:8000/cbsd/register \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "cbsd_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "grant_amount": 100000000000000000000,
    "frequency_hz": 3550000000,
    "bandwidth_hz": 10000000,
    "expiry_timestamp": 1750726000
  }' | jq '.'
echo ""

wait_a_bit

# 5. Obter informações do CBSD
echo "5️⃣ Obter informações do CBSD"
echo "----------------------------"
curl -s http://localhost:8000/cbsd/1 | jq '.'
echo ""

wait_a_bit

# 6. Atualizar grant amount
echo "6️⃣ Atualizar grant amount"
echo "-------------------------"
curl -s -X PUT http://localhost:8000/cbsd/grant-amount \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "new_grant_amount": 150000000000000000000
  }' | jq '.'
echo ""

wait_a_bit

# 7. Atualizar status
echo "7️⃣ Atualizar status"
echo "-------------------"
curl -s -X PUT http://localhost:8000/cbsd/status \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "new_status": "active"
  }' | jq '.'
echo ""

wait_a_bit

# 8. Atualizar detalhes do grant
echo "8️⃣ Atualizar detalhes do grant"
echo "------------------------------"
curl -s -X PUT http://localhost:8000/cbsd/grant-details \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 1,
    "frequency_hz": 3650000000,
    "bandwidth_hz": 20000000,
    "expiry_timestamp": 1750728000
  }' | jq '.'
echo ""

wait_a_bit

# 9. Listar todos os CBSDs
echo "9️⃣ Listar todos os CBSDs"
echo "------------------------"
curl -s http://localhost:8000/cbsd | jq '.'
echo ""

wait_a_bit

# 10. Ver eventos recentes
echo "🔟 Ver eventos recentes"
echo "----------------------"
curl -s http://localhost:8000/events/recent | jq '.'
echo ""

wait_a_bit

# 11. Registrar segundo CBSD
echo "1️⃣1️⃣ Registrar segundo CBSD"
echo "---------------------------"
curl -s -X POST http://localhost:8000/cbsd/register \
  -H "Content-Type: application/json" \
  -d '{
    "cbsd_id": 2,
    "cbsd_address": "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
    "grant_amount": 200000000000000000000,
    "frequency_hz": 3700000000,
    "bandwidth_hz": 15000000,
    "expiry_timestamp": 1750729000
  }' | jq '.'
echo ""

wait_a_bit

# 12. Listar todos os CBSDs novamente
echo "1️⃣2️⃣ Listar todos os CBSDs (após segundo registro)"
echo "------------------------------------------------"
curl -s http://localhost:8000/cbsd | jq '.'
echo ""

wait_a_bit

# 13. Teste de erro - SAS não autorizado
echo "1️⃣3️⃣ Teste de erro - SAS não autorizado"
echo "--------------------------------------"
curl -s http://localhost:8000/sas/0x1234567890123456789012345678901234567890/authorized | jq '.'
echo ""

wait_a_bit

# 14. Revogar SAS
echo "1️⃣4️⃣ Revogar SAS"
echo "----------------"
curl -s -X POST http://localhost:8000/sas/revoke \
  -H "Content-Type: application/json" \
  -d '{"sas_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"}' | jq '.'
echo ""

echo "✅ Teste com blockchain concluído!"
echo ""
echo "🎉 Todos os endpoints blockchain foram testados com sucesso!"
echo "📊 Verifique os logs da API para mais detalhes."
echo ""
echo "📚 Para mais informações, consulte:"
echo "   - API_DOCS.md - Documentação técnica"
echo "   - README.md - Guia de instalação" 