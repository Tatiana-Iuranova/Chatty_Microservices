from pydantic_settings import BaseSettings, SettingsConfigDict

class SubscriptSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env.local', extra='ignore', case_sensitive=False
    )

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    @property
    def async_database_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

settings = SubscriptSettings()

if __name__ == '__main__':
    print(settings.model_dump())
    print(settings.async_database_url)