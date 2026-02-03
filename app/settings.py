from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# 1. Calculate the project root directory
# __file__ = .../Local Save/app/settings.py
# .parent  = .../Local Save/app
# .parent  = .../Local Save (The Root)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Point to the .env file inside the "Server" folder
ENV_PATH = BASE_DIR / "Server" / ".env"

class Settings(BaseSettings):
    # 3. Tell Pydantic to use the absolute path we calculated
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, 
        extra="ignore"
    )

    ORIGIN_BASE_URL: str = "http://127.0.0.1:5000"
    WAF_MODE: str = "protect"

    LOG_DIR: str = "logs"
    ACCESS_LOG_FILE: str = "access.jsonl"

    DB_HOST: str = "127.0.0.1"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"  # This will be overwritten by .env
    DB_NAME: str = "neurowaf_db"
    DB_PORT: int = 3306


settings = Settings()