import logging
import schedule
import time
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, pipeline: Any, timezone: Any):
        self.pipeline = pipeline
        self.timezone = timezone

    def schedule_jobs(self) -> None:
        schedule.every(1).hours.do(self._refresh_token)
        schedule.every(3).minutes.do(self._fetch_intraday)
        schedule.every(20).minutes.do(self._fetch_battery)
        schedule.every(3).hours.do(self._fetch_daily_30d)
        schedule.every(4).hours.do(self._fetch_daily_100d)
        schedule.every(6).hours.do(self._fetch_daily_365d)
        schedule.every(1).hours.do(self._fetch_activities)

    def _refresh_token(self) -> None:
        logger.info("Refreshing Fitbit token...")
        self.pipeline.client.auth.refresh()
        logger.info("Token refreshed")

    def _fetch_intraday(self) -> None:
        logger.info("Fetching intraday data...")
        self.pipeline.run_daily(days_back=1)

    def _fetch_battery(self) -> None:
        logger.info("Fetching battery level...")
        battery = self.pipeline.client.get_battery_level(self.pipeline.device_name)
        if battery:
            logger.info(f"Battery: {battery['battery_level']}%")

    def _fetch_daily_30d(self) -> None:
        logger.info("Fetching 30-day data...")
        end = datetime.now(self.timezone)
        start = end.replace(day=1)
        self.pipeline.fetcher.fetch_daily_aggregates(
            start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        )

    def _fetch_daily_100d(self) -> None:
        logger.info("Fetching 100-day data...")

    def _fetch_daily_365d(self) -> None:
        logger.info("Fetching 365-day data...")

    def _fetch_activities(self) -> None:
        logger.info("Fetching activities...")

    def run(self) -> None:
        logger.info("Starting scheduler...")
        self.schedule_jobs()

        while True:
            schedule.run_pending()
            time.sleep(30)
