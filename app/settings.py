from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ORIGIN_BASE_URL: str = "http://127.0.0.1:5000"
    WAF_MODE: str = "shadow"

    LOG_DIR: str = "logs"
    ACCESS_LOG_FILE: str = "access.jsonl"



settings = Settings()
