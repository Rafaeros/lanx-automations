from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LOGIN_URL: str
    HOME_URL: str
    PENDING_ORDER_URL: str
    USERNAME: str
    PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()