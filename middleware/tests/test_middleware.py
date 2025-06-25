#!/usr/bin/env python3
"""
Script de teste para o middleware SASSharedRegistry
"""

import os
import sys
import asyncio

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    
    try:
        from src.config.settings import settings
        print("✅ Config importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar config: {e}")
        return False
    
    try:
        from src.blockchain.blockchain import Blockchain
        print("✅ Blockchain importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar blockchain: {e}")
        return False
    
    try:
        from src.handlers.handlers import EVENT_HANDLERS
        print("✅ Handlers importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar handlers: {e}")
        return False
    
    try:
        from src.repository.repository import CBSDRepository
        print("✅ Repository importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar repository: {e}")
        return False
    
    return True

def test_config():
    """Testa se as configurações estão definidas"""
    print("\n🔧 Testando configurações...")
    
    try:
        from src.config.settings import settings
        
        # Verificar se as variáveis de ambiente estão definidas
        required_vars = ['RPC_URL', 'CONTRACT_ADDRESS', 'OWNER_PRIVATE_KEY', 'CHAIN_ID']
        
        for var in required_vars:
            if hasattr(settings, var):
                value = getattr(settings, var)
                if value:
                    print(f"✅ {var}: {str(value)[:20]}...")
                else:
                    print(f"⚠️  {var}: vazio")
            else:
                print(f"❌ {var}: não encontrado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar configurações: {e}")
        return False

def test_abi():
    """Testa se o ABI está presente"""
    print("\n📄 Testando ABI...")
    
    abi_path = os.path.join(os.path.dirname(__file__), 'abi', 'SASSharedRegistry.json')
    
    if os.path.exists(abi_path):
        print(f"✅ ABI encontrado em: {abi_path}")
        
        try:
            import json
            with open(abi_path, 'r') as f:
                abi = json.load(f)
            print(f"✅ ABI carregado com sucesso ({len(abi)} itens)")
            return True
        except Exception as e:
            print(f"❌ Erro ao carregar ABI: {e}")
            return False
    else:
        print(f"❌ ABI não encontrado em: {abi_path}")
        return False

async def test_blockchain_connection():
    """Testa conexão com a blockchain (sem enviar transações)"""
    print("\n🔗 Testando conexão com blockchain...")
    
    try:
        from src.blockchain.blockchain import Blockchain
        
        # Tentar criar instância (vai falhar se não conseguir conectar)
        bc = Blockchain()
        print("✅ Instância Blockchain criada com sucesso")
        
        # Testar algumas funções básicas
        try:
            latest_block = bc.get_latest_block()
            print(f"✅ Último bloco: {latest_block}")
        except Exception as e:
            print(f"⚠️  Não foi possível obter último bloco: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar com blockchain: {e}")
        print("💡 Certifique-se de que o Besu está rodando e as configurações estão corretas")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do middleware SASSharedRegistry\n")
    
    # Teste 1: Imports
    if not test_imports():
        print("\n❌ Teste de imports falhou")
        return False
    
    # Teste 2: Configurações
    if not test_config():
        print("\n❌ Teste de configurações falhou")
        return False
    
    # Teste 3: ABI
    if not test_abi():
        print("\n❌ Teste de ABI falhou")
        return False
    
    # Teste 4: Conexão com blockchain
    try:
        asyncio.run(test_blockchain_connection())
    except Exception as e:
        print(f"❌ Teste de conexão falhou: {e}")
    
    print("\n✅ Testes básicos concluídos!")
    print("\n📋 Próximos passos:")
    print("1. Configure o arquivo .env com valores reais")
    print("2. Certifique-se de que o Besu está rodando")
    print("3. Execute: python main.py")
    
    return True

if __name__ == "__main__":
    main() 