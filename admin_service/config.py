from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Загружаем общие переменные окружения
load_dotenv(dotenv_path='.env.local', override=True)

# Теперь можно загрузить специфические для этого микросервиса переменные окружения
load_dotenv(dotenv_path='./.env.local',
            override=True)  # Для микросервиса admin_service


class AdminSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env.local',
        extra='ignore',
        case_sensitive=False
    )

    # PostgreSQL database settings

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    # # Other settings (optional)
    # debug: bool = False

    # @property
    # def database_url(self) -> str:
    #     """Construct the async database URL."""
    #     if self.db_password:
    #         return (
    #             f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:'
    #             f'{self.db_port}/{self.db_name}'
    #         )
    #     else:
    #         return (
    #             f'postgresql://{self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}'
    #         )

    @property
    def async_database_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'


settings = AdminSettings()

if __name__ == '__main__':
    print(settings.model_dump())
    print(settings.async_database_url)
