from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class SleepFeatures:
    date: str
    device: str
    total_minutes_asleep: int
    total_minutes_in_bed: int
    efficiency: float
    minutes_light: int
    minutes_rem: int
    minutes_deep: int
    minutes_awake: int
    minutes_after_wakeup: int
    minutes_to_fall_asleep: int
    waso: int  # Wake After Sleep Onset
    sleep_midpoint_minutes: Optional[float] = None
    sleep_regularity_index: Optional[float] = None


def extract_sleep_features(sleep_record: dict[str, Any], date: str, device: str) -> SleepFeatures:
    levels = sleep_record.get("levels", {})
    summary = levels.get("summary", {})

    minutes_asleep = sleep_record.get("minutesAsleep", 0)
    minutes_in_bed = sleep_record.get("timeInBed", 0)
    efficiency = sleep_record.get("efficiency", 0)
    minutes_awake = sleep_record.get("minutesAwake", 0)
    minutes_after_wakeup = sleep_record.get("minutesAfterWakeup", 0)
    minutes_to_fall_asleep = sleep_record.get("minutesToFallAsleep", 0)

    waso = minutes_after_wakeup

    light = summary.get("light", {})
    rem = summary.get("rem", {})
    deep = summary.get("deep", {})

    minutes_light = light.get("minutes", 0) or rem.get("minutes", 0)
    minutes_rem = rem.get("minutes", 0)
    minutes_deep = deep.get("minutes", 0)

    start_time = sleep_record.get("startTime", "")
    end_time = sleep_record.get("endTime", "")

    sleep_midpoint = None
    if start_time and end_time:
        try:
            start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration = (end - start).total_seconds() / 60
            sleep_midpoint = duration / 2
        except Exception:
            pass

    return SleepFeatures(
        date=date,
        device=device,
        total_minutes_asleep=minutes_asleep,
        total_minutes_in_bed=minutes_in_bed,
        efficiency=efficiency,
        minutes_light=minutes_light,
        minutes_rem=minutes_rem,
        minutes_deep=minutes_deep,
        minutes_awake=minutes_awake,
        minutes_after_wakeup=minutes_after_wakeup,
        minutes_to_fall_asleep=minutes_to_fall_asleep,
        waso=waso,
        sleep_midpoint_minutes=sleep_midpoint,
    )


def calculate_sleep_score(features: SleepFeatures) -> float:
    """
    Calculate a sleep score (0-100) based on multiple factors:
    - Efficiency (30%)
    - Duration (25%)
    - REM percentage (15%)
    - Deep percentage (15%)
    - Time to fall asleep (10%)
    - WASO (5%)
    """
    efficiency_score = min(features.efficiency / 100 * 30, 30)

    target_minutes = 480  # 8 hours
    duration = features.total_minutes_asleep
    if duration >= target_minutes:
        duration_score = 25
    else:
        duration_score = (duration / target_minutes) * 25

    total_sleep = features.total_minutes_asleep
    if total_sleep > 0:
        rem_pct = (features.minutes_rem / total_sleep) * 100
        deep_pct = (features.minutes_deep / total_sleep) * 100

        rem_score = min(rem_pct / 25 * 15, 15)  # Target ~25%
        deep_score = min(deep_pct / 20 * 15, 15)  # Target ~20%
    else:
        rem_score = 0
        deep_score = 0

    if features.minutes_to_fall_asleep <= 15:
        latency_score = 10
    elif features.minutes_to_fall_asleep <= 30:
        latency_score = 5
    else:
        latency_score = 0

    waso_score = max(5 - (features.waso / 10), 0)

    total = efficiency_score + duration_score + rem_score + deep_score + latency_score + waso_score

    return round(total, 1)


def calculate_sleep_regularity_index(
    sleep_records: list[SleepFeatures], window_days: int = 7
) -> float:
    """
    Calculate sleep regularity index over a window.
    Based on variance in sleep onset and offset times.
    Lower is more regular.
    """
    if len(sleep_records) < window_days:
        return 0.0

    return 0.0  # Placeholder - requires actual timestamps
