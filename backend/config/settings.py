from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Customer 360 API"
    debug: bool = False
    jwt_secret_key: str = "your_super_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
