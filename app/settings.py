from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ORIGIN_BASE_URL: str = "http://127.0.0.1:5000" # web app to protect / forward traffic to
    WAF_MODE: str = "protect" # shadow determine what the WAF should do based on the rules, protect activate the policy and block using the rules

    LOG_DIR: str = "logs"
    ACCESS_LOG_FILE: str = "access.jsonl"

    DB_HOST: str = "127.0.0.1"
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "NeuroWAF_db"
    DB_PORT: int = 3306

settings = Settings()
