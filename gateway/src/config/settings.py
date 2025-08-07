"""
Configuration settings for the SAS Blockchain Registry Middleware
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Blockchain settings
    RPC_URL: str = "http://127.0.0.1:8545"
    CONTRACT_ADDRESS: str = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
    OWNER_PRIVATE_KEY: str = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    CHAIN_ID: int = 1337
    GAS_LIMIT: int = 3000000
    
    # Performance settings
    GAS_PRICE: int = 20000000000
    MAX_PRIORITY_FEE: int = 1000000000
    BATCH_SIZE: int = 10
    ASYNC_TRANSACTIONS: bool = True
    CACHE_ENABLED: bool = True
    CONNECTION_POOL_SIZE: int = 10
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Polling
    POLLING_INTERVAL: int = 2
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Permite campos extras

# Global settings instance
settings = Settings() 