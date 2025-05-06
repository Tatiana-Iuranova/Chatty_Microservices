from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv('.env.local', override=True)


class AdminSettings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    secret_key: str  # 👈 Должно соответствовать ключу из .env.local
    algorithm: str   # 👈 Также

    model_config = SettingsConfigDict(
        env_file=".env.local",
        env_prefix="",  # 👈 Позволяет считывать переменные без префикса
        extra='ignore',
        case_sensitive=False
    )

    @property
    def async_database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.db_user}:{self.db_password}'
            f'@{self.db_host}:{self.db_port}/{self.db_name}'
        )


settings = AdminSettings()

if __name__ == "__main__":
    print(settings.model_dump())
