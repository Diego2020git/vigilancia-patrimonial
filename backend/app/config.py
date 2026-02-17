from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Vigilância Patrimonial"
    secret_key: str = "change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    cors_origin: str = "http://localhost:5173"
    database_url: str = "sqlite:///app.db"


settings = Settings()
