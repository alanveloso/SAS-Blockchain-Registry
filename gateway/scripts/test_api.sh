#!/bin/bash

echo "🧪 Teste Básico da API SAS Shared Registry (Sem Blockchain)"
echo "=========================================================="
echo ""

# Verificar se jq está instalado
if ! command -v jq &> /dev/null; then
    echo "❌ jq não está instalado. Instalando..."
    sudo apt-get update && sudo apt-get install -y jq
fi

# Função para aguardar um pouco entre requests
wait_a_bit() {
    echo "⏳ Aguardando 2 segundos..."
    sleep 2
}

# 1. Health Check
echo "1️⃣ Health Check"
echo "---------------"
curl -s http://localhost:9000/health | jq '.'
echo ""

wait_a_bit

# 2. Endpoint raiz
echo "2️⃣ Endpoint raiz"
echo "----------------"
curl -s http://localhost:9000/ | jq '.'
echo ""

wait_a_bit

# 3. Ver estatísticas
echo "3️⃣ Ver estatísticas"
echo "-------------------"
curl -s http://localhost:9000/stats | jq '.'
echo ""

wait_a_bit

# 4. Ver eventos recentes
echo "4️⃣ Ver eventos recentes"
echo "----------------------"
curl -s http://localhost:9000/events/recent | jq '.'
echo ""

wait_a_bit

# 5. Verificar SAS não autorizado
echo "5️⃣ Verificar SAS não autorizado"
echo "-------------------------------"
curl -s http://localhost:9000/sas/0x1234567890123456789012345678901234567890/authorized | jq '.'
echo ""

echo "✅ Teste básico concluído!"
echo ""
echo "📋 Resultado:"
echo "   - ✅ Endpoints que funcionam sem blockchain testados"
echo "   - ⚠️  Endpoints que precisam de blockchain foram pulados"
echo ""
echo "🚀 Para testar com blockchain:"
echo "   1. Iniciar Hardhat: npx hardhat node"
echo "   2. Deploy contrato: npx hardhat run scripts/deploy-sas-shared-registry.js --network localhost"
echo "   3. Atualizar .env com endereço do contrato"
echo "   4. Reiniciar API: python3 run.py"
echo "   5. Executar teste completo: ./scripts/test_sas_sas.sh"
echo ""
echo "📚 Documentação disponível em:"
echo "   - docs/API_DOCS.md"
echo "   - README.md" 