from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    RPC_URL: str = Field(..., description="URL do RPC do Besu")
    CONTRACT_ADDRESS: str = Field(..., description="Endereço do contrato SASSharedRegistry")
    OWNER_PRIVATE_KEY: str = Field(..., description="Chave privada do owner")
    CHAIN_ID: int = Field(default=1337, description="Chain ID da rede Besu")
    
    # Configurações opcionais
    GAS_LIMIT: int = Field(default=3000000, description="Gas limit padrão para transações")
    POLLING_INTERVAL: int = Field(default=2, description="Intervalo de polling em segundos")
    LOG_LEVEL: str = Field(default="INFO", description="Nível de logging")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()