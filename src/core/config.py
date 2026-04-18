from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./fit_tracker.db"
    PROJECT_NAME: str = "Fit-Tracker"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
