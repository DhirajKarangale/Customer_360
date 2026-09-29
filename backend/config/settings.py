from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Customer 360 API"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
