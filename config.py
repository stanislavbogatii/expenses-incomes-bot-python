from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings (BaseSettings):
    bot_token: SecretStr
    mongo_url: str
    admin_ids: List[int]
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )
    

config = Settings()