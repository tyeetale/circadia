import streamlit as st
import pandas as pd
from pathlib import Path

from circadia.storage import DuckDBStorage
from circadia.features import (
    calculate_sleep_score,
    calculate_activity_score,
    calculate_recovery_score,
)
from circadia.features.composite import get_readiness_status


st.set_page_config(page_title="Circadia Dashboard", layout="wide")

st.title("🌙 Circadia - Health Metrics Dashboard")

DB_PATH = Path("./data/circadia.duckdb")

if not DB_PATH.exists():
    st.error("No database found. Run the pipeline first!")
    st.stop()

storage = DuckDBStorage(DB_PATH)

st.sidebar.header("Date Range")
days = st.sidebar.slider("Days to display", 7, 90, 30)

query = f"""
SELECT * FROM sleep_summary
ORDER BY date DESC
LIMIT {days}
"""
sleep_df = storage.execute(query).df()

query = f"""
SELECT * FROM daily_summary
ORDER BY date DESC
LIMIT {days}
"""
activity_df = storage.execute(query).df()

query = f"""
SELECT * FROM resting_hr
ORDER BY date DESC
LIMIT {days}
"""
rhr_df = storage.execute(query).df()

query = f"""
SELECT * FROM hrv
ORDER BY date DESC
LIMIT {days}
"""
hrv_df = storage.execute(query).df()

st.header("📊 Today's Scores")

col1, col2, col3, col4 = st.columns(4)

if not sleep_df.empty:
    latest_sleep = sleep_df.iloc[0]
    sleep_score = calculate_sleep_score(
        type(
            "obj",
            (),
            {
                "total_minutes_asleep": latest_sleep.get("minutes_asleep", 0),
                "total_minutes_in_bed": latest_sleep.get("minutes_in_bed", 0),
                "efficiency": latest_sleep.get("efficiency", 0),
                "minutes_light": latest_sleep.get("minutes_light", 0),
                "minutes_rem": latest_sleep.get("minutes_rem", 0),
                "minutes_deep": latest_sleep.get("minutes_deep", 0),
                "minutes_to_fall_asleep": latest_sleep.get("minutes_to_fall_asleep", 0),
                "waso": latest_sleep.get("minutes_after_wakeup", 0),
            },
        )()
    )
    col1.metric("Sleep Score", f"{sleep_score:.0f}/100")
    col1.caption(
        f"Duration: {latest_sleep.get('minutes_asleep', 0)}min | Efficiency: {latest_sleep.get('efficiency', 0)}%"
    )

if not activity_df.empty:
    latest_activity = activity_df.iloc[0]
    activity_score = latest_activity.get("steps", 0) / 100
    activity_score = min(activity_score, 100)
    col2.metric("Activity", f"{latest_activity.get('steps', 0):,} steps")
    col2.caption(f"Calories: {latest_activity.get('calories', 0):.0f}")

if not rhr_df.empty:
    latest_rhr = rhr_df.iloc[0]
    col3.metric("Resting HR", f"{latest_rhr.get('value', 'N/A')} bpm")

if not hrv_df.empty:
    latest_hrv = hrv_df.iloc[0]
    col4.metric("HRV (RMSSD)", f"{latest_hrv.get('daily_rmssd', 'N/A')}")

st.divider()

st.header("📈 Trends")

tab1, tab2, tab3 = st.tabs(["Sleep", "Activity", "Recovery"])

with tab1:
    if not sleep_df.empty:
        sleep_df = sleep_df.sort_values("date")
        st.line_chart(
            sleep_df.set_index("date")[
                ["minutes_asleep", "minutes_deep", "minutes_rem", "minutes_light"]
            ]
        )
        st.caption("Minutes: Total asleep (blue), Deep (green), REM (orange), Light (red)")
    else:
        st.info("No sleep data available")

with tab2:
    if not activity_df.empty:
        activity_df = activity_df.sort_values("date")
        st.line_chart(activity_df.set_index("date")[["steps"]])
    else:
        st.info("No activity data available")

with tab3:
    if not rhr_df.empty:
        rhr_df = rhr_df.sort_values("date")
        st.line_chart(rhr_df.set_index("date")[["value"]])
    else:
        st.info("No recovery data available")

st.divider()

st.header("📋 Raw Data")

tab_sleep, tab_activity, tab_rhr, tab_hrv = st.tabs(["Sleep", "Activity", "RHR", "HRV"])

with tab_sleep:
    st.dataframe(sleep_df, use_container_width=True)

with tab_activity:
    st.dataframe(activity_df, use_container_width=True)

with tab_rhr:
    st.dataframe(rhr_df, use_container_width=True)

with tab_hrv:
    st.dataframe(hrv_df, use_container_width=True)
