from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

# Obtains value from the environment files.
class Settings(BaseSettings):
    auth_key: SecretStr = Field(alias='openrouter_api_key')
    base_url: str = Field(alias='openrouter_base_url')
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
print("Environment variables:", settings.model_dump())
