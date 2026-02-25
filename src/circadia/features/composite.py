from dataclasses import dataclass
from typing import Any, Optional

from .sleep import SleepFeatures, calculate_sleep_score
from .activity import ActivityFeatures, calculate_activity_score


@dataclass
class RecoveryFeatures:
    date: str
    device: str
    resting_hr: Optional[int]
    hrv_rmssd: Optional[float]
    hrv_deep: Optional[float]
    sleep_score: float
    spo2_avg: Optional[float]
    breathing_rate: Optional[float]
    skin_temp_variation: Optional[float]


def extract_recovery_features(
    hrv_record: dict[str, Any],
    sleep_features: SleepFeatures,
    spo2: Optional[float] = None,
    breathing_rate: Optional[float] = None,
    skin_temp: Optional[float] = None,
    resting_hr: Optional[int] = None,
    date: str = "",
    device: str = "",
) -> RecoveryFeatures:
    hrv_value = hrv_record.get("value", {})
    hrv_rmssd = hrv_value.get("dailyRmssd")
    hrv_deep = hrv_value.get("deepRmssd")

    sleep_score = calculate_sleep_score(sleep_features)

    return RecoveryFeatures(
        date=date,
        device=device,
        resting_hr=resting_hr,
        hrv_rmssd=hrv_rmssd,
        hrv_deep=hrv_deep,
        sleep_score=sleep_score,
        spo2_avg=spo2,
        breathing_rate=breathing_rate,
        skin_temp_variation=skin_temp,
    )


def calculate_recovery_score(features: RecoveryFeatures) -> float:
    """
    Calculate recovery score (0-100) based on:
    - HRV (30%)
    - Resting HR (20%)
    - Sleep quality (30%)
    - SPO2 (10%)
    - Breathing rate (10%)
    """
    if features.hrv_rmssd is None and features.resting_hr is None:
        return 50.0

    hrv_score = 0
    if features.hrv_rmssd is not None:
        if features.hrv_rmssd >= 50:
            hrv_score = 30
        elif features.hrv_rmssd >= 30:
            hrv_score = 20
        elif features.hrv_rmssd >= 20:
            hrv_score = 10
        else:
            hrv_score = 5

    rhr_score = 0
    if features.resting_hr is not None:
        if features.resting_hr <= 50:
            rhr_score = 20
        elif features.resting_hr <= 60:
            rhr_score = 15
        elif features.resting_hr <= 70:
            rhr_score = 10
        else:
            rhr_score = 5

    sleep_score = features.sleep_score * 0.3

    spo2_score = 0
    if features.spo2_avg is not None:
        if features.spo2_avg >= 97:
            spo2_score = 10
        elif features.spo2_avg >= 95:
            spo2_score = 7
        elif features.spo2_avg >= 93:
            spo2_score = 4
        else:
            spo2_score = 0

    br_score = 0
    if features.breathing_rate is not None:
        if 12 <= features.breathing_rate <= 16:
            br_score = 10
        elif 10 <= features.breathing_rate <= 18:
            br_score = 6
        else:
            br_score = 2

    return round(hrv_score + rhr_score + sleep_score + spo2_score + br_score, 1)


def calculate_health_score(
    sleep_features: SleepFeatures,
    activity_features: ActivityFeatures,
    recovery_features: RecoveryFeatures,
) -> float:
    """
    Calculate overall health score (0-100) as weighted average:
    - Recovery (40%) - foundation of health
    - Sleep (35%) - restoration
    - Activity (25%) - movement
    """
    sleep_score = calculate_sleep_score(sleep_features)
    activity_score = calculate_activity_score(activity_features)
    recovery_score = calculate_recovery_score(recovery_features)

    health = recovery_score * 0.4 + sleep_score * 0.35 + activity_score * 0.25

    return round(health, 1)


def get_readiness_status(score: float) -> str:
    """Get textual readiness status based on score."""
    if score >= 80:
        return "Highly Ready"
    elif score >= 60:
        return "Ready"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Low"
    else:
        return "Rest Day"
