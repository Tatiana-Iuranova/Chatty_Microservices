
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local", override=True)

class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.local",
        extra="ignore",
        case_sensitive=False
    )

    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    secret_key: str
    algorithm: str

    @property
    def async_database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

settings = AuthSettings()


if __name__ == '__main__':
    print(settings.model_dump())
    print(settings.async_database_url)