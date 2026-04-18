from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./fit_tracker.db"
    PROJECT_NAME: str = "Fit-Tracker"

    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    TELEGRAM_BOT_TOKEN: str = "your_bot_token"
    JWT_SECRET: str = "your_jwt_secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
