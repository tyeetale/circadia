# Circadia

Health metrics pipeline: Fitbit → DuckDB → ML scoring

## Setup

```bash
# Install dependencies
uv sync

# Copy environment template
cp .env.example .env
```

## Configure

Edit `.env` with your Fitbit OAuth credentials:

```
FITBIT_CLIENT_ID=your_client_id
FITBIT_CLIENT_SECRET=your_client_secret
FITBIT_REFRESH_TOKEN=your_refresh_token
FITBIT_DEVICE_NAME=Charge 6
```

To get OAuth credentials:
1. Go to https://dev.fitbit.com
2. Create an app (type: "Personal" for intraday data access)
3. Note the Client ID and Client Secret
4. Follow the OAuth flow to get a refresh token

## Run

```bash
# Daily sync
uv run python main.py

# Backfill historical data
# Set BACKFILL=true, MANUAL_START_DATE, MANUAL_END_DATE in .env
uv run python main.py
```

## Project Structure

```
src/circadia/
├── config.py         # Configuration loading
├── fitbit/           # Fitbit API client
│   ├── auth.py       # OAuth token management
│   └── client.py     # API calls
├── storage/          # Data storage
│   └── duckdb.py     # DuckDB operations
└── pipeline/         # Data pipeline
    ├── fetcher.py    # Data fetching
    └── scheduler.py # Scheduling

data/
├── raw/              # Raw API responses
├── staging/          # Cleaned data
└── warehouse/       # Analysis-ready
```

## License

BSD-4-Clause
