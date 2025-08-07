from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    RPC_URL: str = Field(..., description="URL do RPC do Besu")
    CONTRACT_ADDRESS: str = Field(..., description="Endereço do contrato SASSharedRegistry")
    OWNER_PRIVATE_KEY: str = Field(..., description="Chave privada do owner")
    CHAIN_ID: int = Field(default=1337, description="Chain ID da rede Besu")
    
    # Configurações opcionais
    GAS_LIMIT: int = Field(default=3000000, description="Gas limit padrão para transações")
    GAS_PRICE: int = Field(default=20000000000, description="Gas price em wei (20 gwei)")
    MAX_PRIORITY_FEE: int = Field(default=1000000000, description="Max priority fee em wei (1 gwei)")
    POLLING_INTERVAL: int = Field(default=2, description="Intervalo de polling em segundos")
    LOG_LEVEL: str = Field(default="INFO", description="Nível de logging")
    
    # Configurações de performance
    BATCH_SIZE: int = Field(default=10, description="Tamanho do batch para transações")
    ASYNC_TRANSACTIONS: bool = Field(default=True, description="Usar transações assíncronas")
    CACHE_ENABLED: bool = Field(default=True, description="Habilitar cache de resultados")
    CONNECTION_POOL_SIZE: int = Field(default=10, description="Tamanho do pool de conexões")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Permite campos extras

settings = Settings()