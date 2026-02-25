# Circadia - Health Metrics Pipeline

## Vision

Personal health metrics pipeline: fetch from Fitbit Charge 6 → store in DuckDB → power ML-driven insights and scoring.

---

## 1. Why InfluxDB? (Original Design)

InfluxDB was used because:

- **Time-series native** - Perfect for heart rate, steps, sleep - data that arrives in sequences with timestamps
- **Grafana integration** - Native InfluxQL queries, dashboards just work
- **Compression** - TSM engine efficiently stores high-frequency data (intraday HR at 1sec granularity)
- **Historical context** - When this project started (pre-2020), DuckDB didn't exist as a mature option

### Why It Falls Short Now

- **Query flexibility** - InfluxQL is limited; DuckDB speaks full SQL
- **Cross-dataset analysis** - Hard to join with external data (weather, calendar, nutrition)
- **ML readiness** - No native ML integration; exporting to Python is clunky
- **Operational overhead** - Separate server process, Docker container management
- **EOL risk** - InfluxDB 1.x is mature but not being actively developed; 2.x/3.x have tradeoffs

---

## 2. Why DuckDB?

| Criteria | InfluxDB | DuckDB |
|----------|----------|--------|
| **Query language** | InfluxQL (limited) | Full SQL |
| **ML integration** | None | Direct Python + pandas + sklearn |
| **File-based** | No (needs server) | Yes - single file, portable |
| **Analytical speed** | Good | Excellent (columnar, vectorized) |
| **Grafana support** | Native | Plugin available |
| **Data export** | Cumbersome | CSV/Parquet trivial |
| **Ecosystem** | Niche | Growing fast (MotherDuck, etc.) |

**Decision**: DuckDB as the primary analytical store. We'll export aggregated data to InfluxDB only if Grafana is strictly required for dashboards.

---

## 3. Modernization Scope

### Infrastructure
- [ ] **No Docker** - Run as Python script with `uv` environment
- [ ] **.env** for configuration (tokens, DB path, scheduling)
- [ ] **DuckDB** as primary data store (`.duckdb` file)
- [ ] **SQLite fallback** - optional, for lighter use

### Code
- [ ] **Python 3.11+** with type hints
- [ ] **httpx** instead of `requests` (async-capable)
- [ ] **uv** for package management (replaces pip)
- [ ] **pydantic** for config validation
- [ ] **python-dotenv** for .env loading
- [ ] **dataclasses** / **attrs** instead of raw dicts

### Fitbit API
- [ ] **Fitbit Charge 6** focus (most recent device)
- [ ] **OAuth 2.0** with token refresh handled gracefully
- [ ] **Rate-limit aware** fetching (150 calls/hour)
- [ ] **Backfill support** for historical data

### Data Model
- [ ] **Parquet** files for raw API responses (immutable)
- [ ] **DuckDB tables** for processed/transformed data
- [ ] Clear separation: `raw/` → `staging/` → `warehouse/`

---

## 4. Feature Extraction (ML Pipeline Ready)

The original script captures ~20 measurements. We'll enhance for ML:

### Sleep Features
| Feature | Source | ML Use |
|---------|--------|--------|
| Total sleep time | Sleep Summary | Prediction target |
| Sleep efficiency % | Sleep Summary | Quality indicator |
| Deep / Light / REM minutes | Sleep Summary | Stage distribution |
| Time to fall asleep | Sleep Summary | Onset latency |
| Wake after sleep onset (WASO) | Calculated | Fragmentation |
| Sleep midpoint | Calculated | Circadian alignment |
| Sleep regularity index | Calculated | Consistency scoring |

### Cardiovascular Features
| Feature | Source | ML Use |
|---------|--------|--------|
| Resting heart rate (RHR) | RestingHR | Recovery indicator |
| HRV (RMSSD, deep) | HRV | Autonomic nervous system |
| Heart rate zones | HR zones | Training load |
| Intraday HRV (SDNN, pNN50) | Future API | Real-time stress |

### Activity Features
| Feature | Source | ML Use |
|---------|--------|--------|
| Daily steps | Total Steps | Activity volume |
| Active minutes (sedentary/light/fairly/very) | Activity Minutes | Intensity distribution |
| Calories burned | calories | Energy expenditure |
| Distance | distance | Activity volume |
| Steps velocity | Calculated | Activity quality |

### Biomarkers
| Feature | Source | ML Use |
|---------|--------|--------|
| SPO2 (avg/min/max) | SPO2 | Respiratory health |
| Skin temperature variation | Skin Temp | Illness detection |
| Breathing rate | BreathingRate | Respiratory patterns |
| Weight | weight | Body composition |
| BMI | bmi | Composition tracking |

### Composite Scores (ML Outputs)
| Score | Inputs | Purpose |
|-------|--------|---------|
| **Sleep Score** | Efficiency, duration, stages, latency | Overall sleep quality |
| **Recovery Score** | RHR, HRV, sleep quality | Morning readiness |
| **Activity Score** | Steps, active minutes, zones | Daily activity level |
| **Health Score** | Composite of all | General wellness |

---

## 5. Implementation Plan

### Phase 1: Foundation
1. Initialize `uv` project with `pyproject.toml`
2. Set up `.env.example` and config loading
3. Create DuckDB schema matching original InfluxDB measurements
4. Build Fitbit OAuth flow (token refresh handling)
5. Write basic API fetcher (single day, all endpoints)

### Phase 2: Data Pipeline
1. Implement scheduled fetching (cron-style, not Docker)
2. Implement backfill mode for historical data
3. Add rate-limit handling (150 calls/hour)
4. Write data to DuckDB (raw JSON → staged → warehouse)
5. Create idempotent writes (upsert logic)

### Phase 3: Feature Engineering
1. Build feature extraction library
2. Compute daily aggregates from intraday data
3. Calculate composite scores
4. Add support for external data (weather, calendar - optional)

### Phase 4: ML Pipeline
1. Set up ML training scaffold (scikit-learn, optional: xgboost)
2. Implement sleep quality prediction model
3. Implement recovery score model
4. Add model evaluation / retraining logic
5. Create scoring API endpoint (optional: FastAPI)

### Phase 5: Visualization (Optional)
1. Grafana with DuckDB plugin (if needed)
2. Or: Streamlit dashboard for quick exploration
3. Or: Export to CSV/Parquet for external tools

---

## 6. Directory Structure

```
circadia/
├── .env.example
├── pyproject.toml
├── uv.lock
├── README.md
├── plan.md
├── src/
│   └── circadia/
│       ├── __init__.py
│       ├── config.py          # .env loading, validation
│       ├── fitbit/
│       │   ├── __init__.py
│       │   ├── client.py       # OAuth, API calls
│       │   ├── auth.py        # Token management
│       │   └── endpoints.py   # Fitbit API endpoints
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── duckdb.py      # DuckDB operations
│       │   └── schema.py      # Table definitions
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── fetcher.py     # Data fetching orchestration
│       │   ├── transformer.py # Raw → staged → warehouse
│       │   └── scheduler.py   # Cron-style scheduling
│       ├── features/
│       │   ├── __init__.py
│       │   ├── sleep.py       # Sleep feature extraction
│       │   ├── activity.py   # Activity features
│       │   └── composite.py  # Score calculations
│       └── ml/
│           ├── __init__.py
│           ├── model.py       # ML model scaffold
│           ├── train.py       # Training pipeline
│           └── predict.py     # Inference
├── data/
│   ├── raw/                   # Raw JSON from Fitbit
│   ├── staging/               # Cleaned, typed data
│   └── warehouse/            # Aggregated, analysis-ready
├── notebooks/                # EDA, model experimentation
└── tests/
    └── ...
```

---

## 7. Open Questions

- [ ] What scheduling mechanism? (cron, while-loop, APScheduler?)
- [ ] Want InfluxDB retained for Grafana compatibility? (Can sync DuckDB → InfluxDB)
- [ ] Preferred ML framework? (sklearn, xgboost, lightgbm, pycaret?)
- [ ] Alerting desired? (Pushover, Discord, email, none?)
- [ ] Target deployment: local machine, VPS, cloud?

---

## 8. Immediate Next Steps

1. ✅ Repo created
2. ⬜ Initialize `uv` project
3. ⬜ Write config + schema
4. ⬜ Implement Fitbit OAuth + basic fetch
5. ⬜ Write to DuckDB

Ready to proceed with Phase 1?
