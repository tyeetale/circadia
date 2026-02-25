# Circadia Initialization

This document captures the creation and design decisions for Circadia, a health metrics pipeline built from the original [fitbit-grafana](https://github.com/arpanghosh8453/fitbit-grafana) project.

## Project Origin

The project started by cloning `git@github.com:arpanghosh8453/fitbit-grafana.git` - a script to fetch data from Fitbit API and store in InfluxDB with Grafana visualization.

## Design Decisions

### Why Not InfluxDB?

1. **Query flexibility** - InfluxQL is limited; DuckDB speaks full SQL
2. **Cross-dataset analysis** - Hard to join with external data (weather, calendar, nutrition)
3. **ML readiness** - No native ML integration; exporting to Python is clunky
4. **Operational overhead** - Separate server process, Docker container management
5. **EOL risk** - InfluxDB 1.x is mature but not being actively developed

### Why DuckDB?

- File-based (single .duckdb file, portable)
- Full SQL support
- Excellent analytical speed (columnar, vectorized)
- Direct Python + pandas + sklearn integration
- Growing ecosystem (MotherDuck, etc.)

### Why No Docker?

- Unnecessary complexity for a personal tool
- Direct Python script execution with `uv` environment
- Simpler dependency management

### Why .env for Tokens?

- Simpler than file-based tokens
- Can be gitignored easily
- Standard practice for credentials

### Why Streamlit Over Grafana?

- Quick, Python-native dashboards
- Modern UI
- Built-in data tables
- Easier to customize

## Brand: Circadia

**Circadia** was chosen as the subbrand for Lunaris:
- Directly tied to circadian rhythms (sleep, recovery, biological cycles)
- Distinct from "Lunaris" but connected - the moon governs our circadian rhythms
- Clean, pronounceable, memorable
- Works as a standalone brand

## Features Extracted

### Sleep Features
- Total sleep time
- Sleep efficiency %
- Deep / Light / REM minutes
- Time to fall asleep (latency)
- Wake After Sleep Onset (WASO)
- Sleep midpoint

### Cardiovascular Features
- Resting heart rate (RHR)
- HRV (RMSSD, deep)
- Heart rate zones

### Activity Features
- Daily steps
- Active minutes (sedentary/light/fairly/very)
- Calories burned
- Distance

### Biomarkers
- SPO2 (avg/min/max)
- Skin temperature variation
- Breathing rate
- Weight / BMI

## Score Calculations

### Sleep Score (0-100)
- Efficiency: 30%
- Duration: 25%
- REM percentage: 15%
- Deep percentage: 15%
- Time to fall asleep: 10%
- WASO: 5%

### Activity Score (0-100)
- Steps: 35%
- Active minutes: 35%
- Intensity distribution: 20%
- Zone minutes: 10%

### Recovery Score (0-100)
- HRV: 30%
- Resting HR: 20%
- Sleep quality: 30%
- SPO2: 10%
- Breathing rate: 10%

### Health Score (0-100)
- Recovery: 40%
- Sleep: 35%
- Activity: 25%

## Project Structure

```
circadia/
├── src/circadia/
│   ├── config.py          # .env loading, pydantic validation
│   ├── fitbit/
│   │   ├── auth.py        # OAuth token management
│   │   └── client.py      # Fitbit API client (httpx)
│   ├── storage/
│   │   └── duckdb.py     # DuckDB operations + schema
│   ├── pipeline/
│   │   ├── fetcher.py    # Data fetching orchestration
│   │   └── scheduler.py  # Cron-style scheduling
│   ├── features/
│   │   ├── sleep.py      # Sleep feature extraction
│   │   ├── activity.py   # Activity features
│   │   └── composite.py  # Score calculations
│   └── ml/
│       ├── model.py       # ML model scaffold (sklearn)
│       ├── train.py       # Training pipeline
│       └── predict.py     # Inference
├── data/
│   ├── raw/              # Raw API responses (JSON)
│   ├── staging/          # Cleaned data
│   └── warehouse/        # Aggregated, analysis-ready
├── dashboard.py          # Streamlit dashboard
├── main.py              # Entry point
├── pyproject.toml       # uv config
├── .env.example         # Config template
└── plan.md              # Implementation plan
```

## Dependencies

- `httpx` - Async-capable HTTP client
- `pydantic` + `pydantic-settings` - Config validation
- `python-dotenv` - .env loading
- `duckdb` - Database
- `pandas` - Data manipulation
- `scikit-learn` - ML
- `streamlit` - Dashboard
- `schedule` - Scheduling

## Usage

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Add Fitbit OAuth credentials

# Run pipeline (daily sync)
uv run python main.py

# Run dashboard
uv run streamlit run dashboard.py
```

## Fitbit OAuth Setup

1. Go to https://dev.fitbit.com
2. Create an app (type: "Personal" for intraday data access)
3. Note the Client ID and Client Secret
4. Follow the OAuth flow to get a refresh token

## Schema Mapping

Original InfluxDB → DuckDB:

| InfluxDB Measurement | DuckDB Table | Fields |
|---------------------|--------------|--------|
| HeartRate_Intraday | heart_rate_intraday | timestamp, device, value |
| Sleep Summary | sleep_summary | date, device, is_main_sleep, efficiency, minutes_asleep, etc. |
| RestingHR | resting_hr | date, device, value |
| HRV | hrv | date, device, daily_rmssd, deep_rmssd |
| SPO2 | spo2 | date, device, avg, min, max |
| Activity Minutes | activity_minutes | date, device, minutes_sedentary, etc. |
| Daily Summary | daily_summary | date, device, steps, calories, distance |

## Integration with Lunaris

Circadia is a git submodule of the Lunaris project:

```
lunaris/
├── circadia/          ← submodule
└── ...
```

---

*Created: February 2026*
*Based on: fitbit-grafana by arpanghosh8453*
