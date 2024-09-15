import logging.config
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    flight_loader_queue = "flight-put"
    date_fmt: str = "%Y-%m-%d"
    cloudamqp_url: Optional[str] = "amqp://guest:guest@localhost:5672/%2F"

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"


class Paths(BaseSettings):
    base_path: Path = Path(__file__).parent
    data_path: Path = base_path / "data"
    test_data_path: Path = base_path / "test_data"

    def __init__(self, **values: Any):
        super().__init__(**values)

        self.data_path.mkdir(exist_ok=True)
        self.test_data_path.mkdir(exist_ok=True)


settings = Settings()
paths = Paths()

logging.config.fileConfig(
    paths.base_path / "logging.ini", disable_existing_loggers=True
)
