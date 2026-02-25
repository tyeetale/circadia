import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from ..fitbit import FitbitAuth, FitbitClient
from ..storage import DuckDBStorage

logger = logging.getLogger(__name__)


class DataFetcher:
    def __init__(
        self,
        client: FitbitClient,
        storage: DuckDBStorage,
        device_name: str,
        timezone: Any,
        raw_data_dir: Path = Path("./data/raw"),
    ):
        self.client = client
        self.storage = storage
        self.device_name = device_name
        self.timezone = timezone
        self.raw_data_dir = raw_data_dir
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

    def _save_raw(self, endpoint: str, date: str, data: dict[str, Any]) -> None:
        filepath = self.raw_data_dir / f"{endpoint}_{date}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def fetch_day(self, date: str) -> None:
        logger.info(f"Fetching data for {date}")

        intraday_hr = self.client.get_heart_rate_intraday(date, "1sec")
        self._save_raw("heart_rate_intraday", date, intraday_hr)

        intraday_steps = self.client.get_steps_intraday(date, "1min")
        self._save_raw("steps_intraday", date, intraday_steps)

        battery = self.client.get_battery_level(self.device_name)
        if battery:
            logger.info(f"Battery level: {battery['battery_level']}")

    def fetch_range(self, start_date: str, end_date: str) -> None:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        current = start
        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            self.fetch_day(date_str)
            current += timedelta(days=1)

    def fetch_daily_aggregates(self, start_date: str, end_date: str) -> dict[str, Any]:
        results = {}

        try:
            hrv = self.client.get_hrv(start_date, end_date)
            results["hrv"] = hrv.get("hrv", [])
        except Exception as e:
            logger.error(f"Failed to fetch HRV: {e}")

        try:
            br = self.client.get_breathing_rate(start_date, end_date)
            results["breathing_rate"] = br.get("br", [])
        except Exception as e:
            logger.error(f"Failed to fetch breathing rate: {e}")

        try:
            spo2 = self.client.get_spo2(start_date, end_date)
            results["spo2"] = spo2
        except Exception as e:
            logger.error(f"Failed to fetch SPO2: {e}")

        try:
            weight = self.client.get_weight(start_date, end_date)
            results["weight"] = weight.get("weight", [])
        except Exception as e:
            logger.error(f"Failed to fetch weight: {e}")

        try:
            sleep = self.client.get_sleep(start_date, end_date)
            results["sleep"] = sleep.get("sleep", [])
        except Exception as e:
            logger.error(f"Failed to fetch sleep: {e}")

        for activity in [
            "minutesSedentary",
            "minutesLightlyActive",
            "minutesFairlyActive",
            "minutesVeryActive",
        ]:
            try:
                data = self.client.get_activity_minutes(start_date, end_date, activity)
                results[activity] = data.get(f"activities-tracker-{activity}", [])
            except Exception as e:
                logger.error(f"Failed to fetch {activity}: {e}")

        for activity in ["distance", "calories", "steps"]:
            try:
                data = self.client.get_activity_minutes(start_date, end_date, activity)
                results[activity] = data.get(f"activities-tracker-{activity}", [])
            except Exception as e:
                logger.error(f"Failed to fetch {activity}: {e}")

        try:
            hr_zones = self.client.get_heart_rate_zones(start_date, end_date)
            results["heart_rate_zones"] = hr_zones.get("activities-heart", [])
        except Exception as e:
            logger.error(f"Failed to fetch HR zones: {e}")

        try:
            active_zone = self.client.get_active_zone_minutes(start_date, end_date)
            results["active_zone_minutes"] = active_zone.get("activities-active-zone-minutes", [])
        except Exception as e:
            logger.error(f"Failed to fetch active zone minutes: {e}")

        return results


class Pipeline:
    def __init__(
        self,
        client: FitbitClient,
        storage: DuckDBStorage,
        device_name: str,
        timezone: Any,
    ):
        self.client = client
        self.storage = storage
        self.device_name = device_name
        self.timezone = timezone
        self.fetcher = DataFetcher(client, storage, device_name, timezone)

    def run_daily(self, days_back: int = 1) -> None:
        end_date = datetime.now(self.timezone)
        start_date = end_date - timedelta(days=days_back)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        logger.info(f"Running daily fetch from {start_str} to {end_str}")

        self.fetcher.fetch_range(start_str, end_str)
        self.fetcher.fetch_daily_aggregates(start_str, end_str)

        logger.info("Daily fetch complete")

    def run_backfill(self, start_date: str, end_date: str) -> None:
        logger.info(f"Running backfill from {start_date} to {end_date}")
        self.fetcher.fetch_range(start_date, end_date)
        self.fetcher.fetch_daily_aggregates(start_date, end_date)
        logger.info("Backfill complete")
