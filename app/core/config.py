from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Communication Agent API"
    DEBUG: bool = True
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Ollama Settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "yasserrmd/DeepScaleR-1.5B-Preview:latest"
    OLLAMA_MAX_RETRIES: int = 3
    
    # Model Settings
    # DeepScaleR specific configurations
    TEMPERATURE: float = 0.3  # Lower temperature for more precise responses
    MAX_TOKENS: int = 4096    # DeepScaleR supports up to 24K context
    TOP_P: float = 0.9        # Nucleus sampling parameter
    TOP_K: int = 40          # Top-k sampling parameter
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 