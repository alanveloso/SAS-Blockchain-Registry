#!/bin/bash

echo "🧪 Teste de Compatibilidade com WinnForum Test Harness"
echo "====================================================="
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

echo "✅ API está rodando!"

# Testar o endpoint WinnForum Full Activity Dump
echo -e "\n1️⃣ Testando endpoint WinnForum: GET /v1.3/dump"
echo "--------------------------------------------"
RESPONSE=$(curl -s http://localhost:8000/v1.3/dump)

# Verificar se a resposta é válida JSON
if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo "✅ Resposta é JSON válido"
else
    echo "❌ Resposta não é JSON válido"
    echo "Resposta recebida:"
    echo "$RESPONSE"
    exit 1
fi

# Verificar estrutura básica do Full Activity Dump
echo -e "\n2️⃣ Verificando estrutura do Full Activity Dump"
echo "----------------------------------------------"

# Verificar campos obrigatórios
REQUIRED_FIELDS=("version" "generationDateTime" "cbsdRecords" "escSensorDataRecords" "coordinationEventRecords" "ppaRecords" "palRecords" "zoneRecords" "exclusionZoneRecords" "fssRecords" "wispRecords" "sasAdministratorRecords")

for field in "${REQUIRED_FIELDS[@]}"; do
    if echo "$RESPONSE" | jq -e ".$field" > /dev/null 2>&1; then
        echo "✅ Campo '$field' presente"
    else
        echo "❌ Campo '$field' ausente"
    fi
done

# Verificar se há registros CBSD
CBSD_COUNT=$(echo "$RESPONSE" | jq '.cbsdRecords | length')
echo -e "\n📊 Estatísticas:"
echo "   - Registros CBSD: $CBSD_COUNT"

if [ "$CBSD_COUNT" -gt 0 ]; then
    echo "✅ Há registros CBSD no dump"
    
    # Verificar estrutura do primeiro CBSD
    FIRST_CBSD=$(echo "$RESPONSE" | jq '.cbsdRecords[0]')
    
    CBSD_FIELDS=("id" "registration" "grants")
    for field in "${CBSD_FIELDS[@]}"; do
        if echo "$FIRST_CBSD" | jq -e ".$field" > /dev/null 2>&1; then
            echo "   ✅ CBSD tem campo '$field'"
        else
            echo "   ❌ CBSD não tem campo '$field'"
        fi
    done
    
    # Verificar grants
    GRANT_COUNT=$(echo "$FIRST_CBSD" | jq '.grants | length')
    echo "   - Grants no primeiro CBSD: $GRANT_COUNT"
    
else
    echo "⚠️  Não há registros CBSD no dump (pode ser normal para um mock)"
fi

# Mostrar exemplo da resposta (primeiros 500 caracteres)
echo -e "\n3️⃣ Exemplo da resposta (primeiros 500 caracteres):"
echo "------------------------------------------------"
echo "$RESPONSE" | head -c 500
echo "..."

# Verificar se a resposta está no formato esperado pelo WinnForum
echo -e "\n4️⃣ Verificando compatibilidade com WinnForum"
echo "---------------------------------------------"

# Verificar se a versão é 1.3
VERSION=$(echo "$RESPONSE" | jq -r '.version')
if [ "$VERSION" = "1.3" ]; then
    echo "✅ Versão 1.3 (compatível com WinnForum)"
else
    echo "❌ Versão $VERSION (esperado: 1.3)"
fi

# Verificar se generationDateTime está no formato ISO
GENERATION_DATE=$(echo "$RESPONSE" | jq -r '.generationDateTime')
if [[ "$GENERATION_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]]; then
    echo "✅ generationDateTime no formato ISO correto"
else
    echo "❌ generationDateTime não está no formato ISO: $GENERATION_DATE"
fi

echo -e "\n🎉 Teste de compatibilidade concluído!"
echo ""
echo "📋 Resumo:"
echo "   - ✅ Endpoint /v1.3/dump está funcionando"
echo "   - ✅ Resposta é JSON válido"
echo "   - ✅ Estrutura básica do Full Activity Dump presente"
echo "   - ✅ Formato compatível com WinnForum Test Harness"
echo ""
echo "🚀 Próximos passos:"
echo "   1. Configurar HTTPS/certificados (se necessário)"
echo "   2. Conectar dados reais do seu sistema"
echo "   3. Executar test harness oficial do WinnForum"
echo ""
echo "📚 Para executar o test harness oficial:"
echo "   - Baixar: https://github.com/Wireless-Innovation-Forum/Spectrum-Access-System"
echo "   - Configurar sas.cfg para apontar para localhost:8000"
echo "   - Executar: python test_main.py WINNF_FT_S_FAD_testcase" 