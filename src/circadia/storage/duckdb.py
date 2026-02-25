from datetime import datetime
from pathlib import Path

from typing import Any

import duckdb


def get_schema() -> list[str]:
    return [
        """
        CREATE TABLE IF NOT EXISTS heart_rate_intraday (
            timestamp TIMESTAMP NOT NULL,
            device VARCHAR,
            value INTEGER,
            PRIMARY KEY (timestamp, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS steps_intraday (
            timestamp TIMESTAMP NOT NULL,
            device VARCHAR,
            value INTEGER,
            PRIMARY KEY (timestamp, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sleep_summary (
            date DATE NOT NULL,
            device VARCHAR,
            is_main_sleep BOOLEAN,
            efficiency INTEGER,
            minutes_after_wakeup INTEGER,
            minutes_asleep INTEGER,
            minutes_to_fall_asleep INTEGER,
            minutes_in_bed INTEGER,
            minutes_awake INTEGER,
            minutes_light INTEGER,
            minutes_rem INTEGER,
            minutes_deep INTEGER,
            PRIMARY KEY (date, device, is_main_sleep)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sleep_levels (
            timestamp TIMESTAMP NOT NULL,
            device VARCHAR,
            is_main_sleep BOOLEAN,
            level INTEGER,
            duration_seconds INTEGER,
            PRIMARY KEY (timestamp, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS resting_hr (
            date DATE NOT NULL,
            device VARCHAR,
            value INTEGER,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS hrv (
            date DATE NOT NULL,
            device VARCHAR,
            daily_rmssd DOUBLE,
            deep_rmssd DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS hr_zones (
            date DATE NOT NULL,
            device VARCHAR,
            normal_minutes INTEGER,
            fat_burn_minutes INTEGER,
            cardio_minutes INTEGER,
            peak_minutes INTEGER,
            active_zone_minutes INTEGER,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_minutes (
            date DATE NOT NULL,
            device VARCHAR,
            minutes_sedentary INTEGER,
            minutes_lightly_active INTEGER,
            minutes_fairly_active INTEGER,
            minutes_very_active INTEGER,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_summary (
            date DATE NOT NULL,
            device VARCHAR,
            steps DOUBLE,
            calories DOUBLE,
            distance DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS spo2 (
            date DATE NOT NULL,
            device VARCHAR,
            avg DOUBLE,
            min DOUBLE,
            max DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS spo2_intraday (
            timestamp TIMESTAMP NOT NULL,
            device VARCHAR,
            value DOUBLE,
            PRIMARY KEY (timestamp, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS breathing_rate (
            date DATE NOT NULL,
            device VARCHAR,
            value DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS skin_temperature (
            date DATE NOT NULL,
            device VARCHAR,
            relative_value DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS weight (
            timestamp TIMESTAMP NOT NULL,
            device VARCHAR,
            value DOUBLE,
            bmi DOUBLE,
            PRIMARY KEY (timestamp, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS device_battery (
            last_sync_time TIMESTAMP NOT NULL,
            device VARCHAR,
            level DOUBLE,
            PRIMARY KEY (last_sync_time, device)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS activity_records (
            timestamp TIMESTAMP NOT NULL,
            activity_name VARCHAR,
            active_duration INTEGER,
            average_heart_rate INTEGER,
            calories INTEGER,
            duration INTEGER,
            distance DOUBLE,
            steps INTEGER,
            PRIMARY KEY (timestamp, activity_name)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS gps_data (
            timestamp TIMESTAMP NOT NULL,
            activity_id VARCHAR,
            lat DOUBLE,
            lon DOUBLE,
            altitude DOUBLE,
            distance DOUBLE,
            heart_rate INTEGER,
            speed_kph DOUBLE,
            PRIMARY KEY (timestamp, activity_id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_features (
            date DATE NOT NULL,
            device VARCHAR,
            sleep_score DOUBLE,
            recovery_score DOUBLE,
            activity_score DOUBLE,
            health_score DOUBLE,
            PRIMARY KEY (date, device)
        );
        """,
    ]


class DuckDBStorage:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: duckdb.DuckDBPyConnection | None = None

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = duckdb.connect(str(self.db_path))
        return self._conn

    def init_schema(self) -> None:
        for stmt in get_schema():
            self.conn.execute(stmt)
        self.conn.commit()

    def execute(self, query: str, *args) -> Any:
        return self.conn.execute(query, *args)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
