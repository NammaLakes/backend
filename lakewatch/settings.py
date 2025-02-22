import enum
from pathlib import Path
from tempfile import gettempdir
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())

class LogLevel(str, enum.Enum):
    """Possible log levels."""
    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"

class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured with environment variables.
    """

    # Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    workers_count: int = 1  # Number of Uvicorn workers
    reload: bool = False  # Enable auto-reload in development

    # Environment
    environment: str = "dev"

    # Logging
    log_level: LogLevel = LogLevel.INFO

    # Database (SQLite)
    db_file: Path = TEMP_DIR / "db.sqlite3"
    db_echo: bool = False

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(scheme="sqlite", path=f"///{self.db_file}")

    # RabbitMQ Configuration
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_queue: str = "node_data"

    # API Key Authentication (Set a default key for now)
    api_key: str = "test_api_key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LAKEWATCH_",
        env_file_encoding="utf-8",
    )

# Create settings instance
settings = Settings()
