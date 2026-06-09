from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.DATABASE_USERNAME}"
            f":{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}"
            f":{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USERNAME}"
            f":{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}"
            f":{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")


settings = Settings()
