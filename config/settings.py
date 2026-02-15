from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create a logger instance
logger = logging.getLogger(__name__)

# Obtains value from the environment files.
class Settings(BaseSettings):
    auth_key: SecretStr = Field(alias='openrouter_api_key')
    base_url: str = Field(alias='openrouter_base_url')
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
logging.info("Environment variables:", settings.model_dump())
