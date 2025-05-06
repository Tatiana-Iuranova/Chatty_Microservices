import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Загружаем общие переменные окружения
# Выбираем env-файл в зависимости от окружения (если передан переменной среды)
env_file = os.getenv("ENV_FILE", ".env.local")
load_dotenv(dotenv_path=env_file, override=True)



class PostSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_file,
        extra='ignore',
        case_sensitive=False
    )

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def async_database_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

settings = PostSettings()

if __name__ == '__main__':
    print(settings.model_dump())
    print(settings.async_database_url)