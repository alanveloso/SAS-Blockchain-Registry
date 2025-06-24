#!/bin/bash

echo "🚀 Setup do SAS Blockchain Registry Middleware"
echo "=============================================="

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instalando..."
    sudo apt-get install -y python3-pip
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p abi

# Configurar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "⚙️ Criando arquivo .env..."
    cp env.example .env
    echo "✅ Arquivo .env criado. Edite com suas configurações."
else
    echo "✅ Arquivo .env já existe."
fi

# Tornar scripts executáveis
echo "🔧 Configurando scripts..."
chmod +x scripts/*.sh
chmod +x run.py
chmod +x app.py

echo ""
echo "✅ Setup concluído!"
echo ""
echo "📋 Próximos passos:"
echo "1. Editar o arquivo .env com suas configurações"
echo "2. Iniciar o nó Hardhat: npx hardhat node"
echo "3. Executar a API: python3 run.py"
echo "4. Testar: ./scripts/test_complete_api.sh"
echo ""
echo "📚 Documentação disponível em:"
echo "   - docs/API_DOCS.md"
echo "   - README.md" 