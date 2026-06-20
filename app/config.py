from pydantic import SecretStr, ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: SecretStr
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    model_config = ConfigDict(env_file=".env")

settings = Settings()

print(settings)
