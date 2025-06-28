#!/bin/bash

# Script para gerar TODOS os planos de carga
# SAS Blockchain Registry - Performance Testing

# Adicionar criação do diretório 'plans'
mkdir -p plans

echo "🔧 Gerando TODOS os planos de carga para SAS Blockchain Registry"
echo "================================================================"
echo ""

# Lista de endpoints SAS (incluindo health check)
ENDPOINTS=("authorize" "revoke" "grant" "registration" "relinquishment" "deregistration")
# Lista de TODOS os níveis de carga
LEVELS=("low" "medium" "high" "stress")

# Configurações por nível
declare -A CONFIG
CONFIG[low_threads]="2"
CONFIG[low_loops]="5"
CONFIG[low_ramp]="10"
CONFIG[medium_threads]="5"
CONFIG[medium_loops]="10"
CONFIG[medium_ramp]="20"
CONFIG[high_threads]="15"
CONFIG[high_loops]="20"
CONFIG[high_ramp]="45"
CONFIG[stress_threads]="30"
CONFIG[stress_loops]="30"
CONFIG[stress_ramp]="90"
CONFIG[endurance_threads]="10"
CONFIG[endurance_loops]="50"
CONFIG[endurance_ramp]="60"
CONFIG[endurance_duration]="1800"

# Permitir configuração dinâmica do host e porta via variáveis de ambiente
API_HOST="${API_HOST:-localhost}"
API_PORT="${API_PORT:-9000}"

echo "📋 Gerando planos para:"
echo "   Endpoints: ${ENDPOINTS[@]}"
echo "   Níveis: ${LEVELS[@]}"
echo ""

# Função para gerar plano
generate_plan() {
    local endpoint=$1
    local level=$2
    
    local filename="sas_${endpoint}_${level}.jmx"
    local threads=${CONFIG[${level}_threads]}
    local loops=${CONFIG[${level}_loops]}
    local ramp=${CONFIG[${level}_ramp]}
    local duration=${CONFIG[${level}_duration]:-""}
    
    echo "🔧 Gerando: $filename"
    
    # Determinar endpoint e payload baseado no tipo
    local api_path=""
    local payload=""
    local method="POST"
    
    case $endpoint in
        "health_check")
            api_path="/health"
            payload=""
            method="GET"
            ;;
        "authorize")
            api_path="/sas/authorize"
            payload='{"sas_address":"0x${__RandomString(40,abcdef0123456789,)}"}'
            ;;
        "revoke")
            api_path="/sas/revoke"
            payload='{"sas_address":"0x${__RandomString(40,abcdef0123456789,)}"}'
            ;;
        "grant")
            api_path="/v1.3/grant"
            payload='{"fccId":"TEST-FCC-${__threadNum}-${__UUID}","cbsdSerialNumber":"TEST-CBSD-${__threadNum}-${__UUID}","channelType":"GAA","maxEirp":47,"lowFrequency":3550000000,"highFrequency":3700000000,"requestedMaxEirp":47,"requestedLowFrequency":3550000000,"requestedHighFrequency":3700000000,"grantExpireTime":1750726000}'
            ;;
        "registration")
            api_path="/v1.3/registration"
            payload='{"fccId":"TEST-FCC-${__threadNum}-${__UUID}","cbsdSerialNumber":"TEST-CBSD-${__threadNum}-${__UUID}","userId":"TEST-USER-${__threadNum}","callSign":"TESTCALL${__threadNum}","cbsdCategory":"A","airInterface":"E_UTRA","measCapability":["EUTRA_CARRIER_RSSI"],"eirpCapability":47,"latitude":375000000,"longitude":1224000000,"height":30,"heightType":"AGL","indoorDeployment":false,"antennaGain":15,"antennaBeamwidth":360,"antennaAzimuth":0,"groupingParam":"","cbsdAddress":"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"}'
            ;;
        "relinquishment")
            api_path="/v1.3/relinquishment"
            payload='{"fccId":"TEST-FCC-${__threadNum}-${__UUID}","cbsdSerialNumber":"TEST-CBSD-${__threadNum}-${__UUID}","grantId":"grant_${__threadNum}_${__UUID}"}'
            ;;
        "deregistration")
            api_path="/v1.3/deregistration"
            payload='{"fccId":"TEST-FCC-${__threadNum}-${__UUID}","cbsdSerialNumber":"TEST-CBSD-${__threadNum}-${__UUID}"}'
            ;;
    esac
    
    # Gerar arquivo JMX
    cat > "plans/$filename" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="SAS ${endpoint^} - Carga ${level^}" enabled="true">
      <stringProp name="TestPlan.comments">Benchmark de ${endpoint} SAS com carga ${level} (${threads} usuários, ${loops} iterações)</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="${endpoint^} Thread Group - ${level^}" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">${loops}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">${threads}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">${ramp}</stringProp>
        <boolProp name="ThreadGroup.scheduler">${duration:+true}</boolProp>
        <stringProp name="ThreadGroup.duration">${duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="${endpoint^} SAS" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments">
EOF

    # Adicionar payload apenas se não for GET
    if [ "$method" != "GET" ] && [ -n "$payload" ]; then
        cat >> "plans/$filename" << EOF
              <elementProp name="" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">${payload}</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
              </elementProp>
EOF
    fi

    cat >> "plans/$filename" << EOF
            </collectionProp>
          </elementProp>
          <stringProp name="HTTPSampler.domain">${API_HOST}</stringProp>
          <stringProp name="HTTPSampler.port">${API_PORT}</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">${api_path}</stringProp>
          <stringProp name="HTTPSampler.method">${method}</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
EOF

    # Adicionar headers apenas se não for GET
    if [ "$method" != "GET" ]; then
        cat >> "plans/$filename" << EOF
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Content-Type</stringProp>
                <stringProp name="Header.value">application/json</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree/>
EOF
    fi

    cat >> "plans/$filename" << EOF
          <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Code Assertion" enabled="true">
            <collectionProp name="Asserion.test_strings">
              <stringProp name="49586">200</stringProp>
            </collectionProp>
            <stringProp name="Assertion.custom_message"></stringProp>
            <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
            <boolProp name="Assertion.assume_success">false</boolProp>
            <intProp name="Assertion.test_type">8</intProp>
          </ResponseAssertion>
          <hashTree/>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
EOF

    echo "✅ $filename gerado com sucesso"
}

# Gerar todos os planos
for endpoint in "${ENDPOINTS[@]}"; do
    for level in "${LEVELS[@]}"; do
        generate_plan "$endpoint" "$level"
    done
done

echo ""
echo "🎉 TODOS os planos foram gerados!"
echo "📋 Total de planos criados: $(( ${#ENDPOINTS[@]} * ${#LEVELS[@]} ))"
echo ""
echo "📁 Planos disponíveis:"
echo "   🔵 Carga Baixa: ${#ENDPOINTS[@]} planos"
echo "   🟡 Carga Média: ${#ENDPOINTS[@]} planos"
echo "   🟠 Carga Alta: ${#ENDPOINTS[@]} planos"
echo "   🔴 Stress: ${#ENDPOINTS[@]} planos"
echo "   🟣 Endurance: ${#ENDPOINTS[@]} planos"
echo ""
echo "🚀 Execute: ./scripts/run_load_scenarios.sh para testar todos os cenários" 