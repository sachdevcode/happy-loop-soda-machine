from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./soda_vending.db")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Application Configuration
    app_title: str = os.getenv("APP_TITLE", "Soda Vending Machine API")
    app_description: str = os.getenv("APP_DESCRIPTION", "AI-powered soda vending machine with natural language processing")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]  # Default to allow all origins
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    cors_allow_methods: List[str] = ["*"]  # Default to allow all methods
    cors_allow_headers: List[str] = ["*"]  # Default to allow all headers
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings() 