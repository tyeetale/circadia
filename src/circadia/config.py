from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class FitbitConfig(BaseModel):
    client_id: str = Field(default="", alias="FITBIT_CLIENT_ID")
    client_secret: str = Field(default="", alias="FITBIT_CLIENT_SECRET")
    refresh_token: Optional[str] = Field(default=None, alias="FITBIT_REFRESH_TOKEN")
    access_token: Optional[str] = None
    device_name: str = Field(default="Charge 6", alias="FITBIT_DEVICE_NAME")


class DatabaseConfig(BaseModel):
    path: Path = Field(default=Path("./data/circadia.duckdb"), alias="DUCKDB_PATH")


class SchedulingConfig(BaseModel):
    backfill: bool = Field(default=False, alias="BACKFILL")
    auto_date_range_days: int = Field(default=1, alias="AUTO_DATE_RANGE_DAYS")
    manual_start_date: Optional[str] = Field(default=None, alias="MANUAL_START_DATE")
    manual_end_date: Optional[str] = Field(default=None, alias="MANUAL_END_DATE")


class Config(BaseSettings):
    fitbit: FitbitConfig = Field(default_factory=FitbitConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    scheduling: SchedulingConfig = Field(default_factory=SchedulingConfig)
    timezone: str = Field(default="Automatic", alias="LOCAL_TIMEZONE")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_config() -> Config:
    return Config()
