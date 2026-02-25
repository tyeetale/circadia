import logging
import sys
from pathlib import Path

from circadia.config import get_config
from circadia.fitbit import FitbitAuth, FitbitClient
from circadia.pipeline import Pipeline, Scheduler
from circadia.storage import DuckDBStorage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def main() -> None:
    config = get_config()

    logging.info("Initializing Circadia...")

    if not config.fitbit.client_id or not config.fitbit.client_secret:
        logging.error("Missing FITBIT_CLIENT_ID or FITBIT_CLIENT_SECRET")
        logging.info("Copy .env.example to .env and fill in your Fitbit OAuth credentials")
        return

    db_path = config.database.path
    storage = DuckDBStorage(db_path)
    storage.init_schema()
    logging.info(f"Database initialized at {db_path}")

    auth = FitbitAuth(
        client_id=config.fitbit.client_id,
        client_secret=config.fitbit.client_secret,
        token_path=Path("./data/tokens.json"),
    )

    try:
        auth.initialize(config.fitbit.refresh_token)
    except ValueError as e:
        logging.error(f"Authentication failed: {e}")
        logging.info("Provide FITBIT_REFRESH_TOKEN in .env or run OAuth flow")
        return

    client = FitbitClient(auth, config.fitbit.client_id, config.fitbit.client_secret)

    if config.timezone == "Automatic":
        timezone = client.get_timezone_obj()
    else:
        import pytz

        timezone = pytz.timezone(config.timezone)

    logging.info(f"Using timezone: {timezone}")

    pipeline = Pipeline(client, storage, config.fitbit.device_name, timezone)

    if config.scheduling.backfill:
        start = config.scheduling.manual_start_date
        end = config.scheduling.manual_end_date
        if start and end:
            pipeline.run_backfill(start, end)
        else:
            logging.error("Backfill requires MANUAL_START_DATE and MANUAL_END_DATE")
            return
    else:
        pipeline.run_daily(days_back=config.scheduling.auto_date_range_days)

    logging.info("Starting scheduled updates...")
    scheduler = Scheduler(pipeline, timezone)
    scheduler.run()


if __name__ == "__main__":
    main()
