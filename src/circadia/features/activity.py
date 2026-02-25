from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ActivityFeatures:
    date: str
    device: str
    steps: int
    calories: float
    distance: float
    minutes_sedentary: int
    minutes_lightly_active: int
    minutes_fairly_active: int
    minutes_very_active: int
    active_minutes_total: int
    hr_zone_normal: int
    hr_zone_fat_burn: int
    hr_zone_cardio: int
    hr_zone_peak: int
    active_zone_minutes: int
    resting_hr: Optional[int] = None


def extract_activity_features(
    daily_summary: dict[str, Any],
    activity_minutes: dict[str, Any],
    hr_zones: dict[str, Any],
    resting_hr: Optional[int] = None,
    date: str = "",
    device: str = "",
) -> ActivityFeatures:
    steps = int(daily_summary.get("value", 0))

    calories = daily_summary.get("calories", 0)
    distance = daily_summary.get("distance", 0.0)

    mins_sedentary = activity_minutes.get("minutesSedentary", 0)
    mins_light = activity_minutes.get("minutesLightlyActive", 0)
    mins_fair = activity_minutes.get("minutesFairlyActive", 0)
    mins_very = activity_minutes.get("minutesVeryActive", 0)

    active_total = mins_light + mins_fair + mins_very

    zones = hr_zones.get("value", {}).get("heartRateZones", [])
    zone_normal = 0
    zone_fat_burn = 0
    zone_cardio = 0
    zone_peak = 0

    for zone in zones:
        name = zone.get("name", "")
        mins = zone.get("minutes", 0)
        if name == "Rest":
            zone_normal = mins
        elif name == "Fat Burn":
            zone_fat_burn = mins
        elif name == "Cardio":
            zone_cardio = mins
        elif name == "Peak":
            zone_peak = mins

    azm = hr_zones.get("value", {}).get("activeZoneMinutes", {})

    return ActivityFeatures(
        date=date,
        device=device,
        steps=steps,
        calories=float(calories),
        distance=float(distance),
        minutes_sedentary=mins_sedentary,
        minutes_lightly_active=mins_light,
        minutes_fairly_active=mins_fair,
        minutes_very_active=mins_very,
        active_minutes_total=active_total,
        hr_zone_normal=zone_normal,
        hr_zone_fat_burn=zone_fat_burn,
        hr_zone_cardio=zone_cardio,
        hr_zone_peak=zone_peak,
        active_zone_minutes=azm.get("minutesInActiveZone", 0) if isinstance(azm, dict) else 0,
        resting_hr=resting_hr,
    )


def calculate_activity_score(features: ActivityFeatures) -> float:
    """
    Calculate activity score (0-100) based on:
    - Steps (35%)
    - Active minutes (35%)
    - Intensity distribution (20%)
    - Zone minutes (10%)
    """
    steps_score = 0
    if features.steps >= 10000:
        steps_score = 35
    elif features.steps >= 7500:
        steps_score = 28
    elif features.steps >= 5000:
        steps_score = 21
    elif features.steps >= 2500:
        steps_score = 14
    else:
        steps_score = (features.steps / 2500) * 14

    target_active = 30
    active_score = min((features.active_minutes_total / target_active) * 35, 35)

    intensity_score = 0
    if features.active_minutes_total > 0:
        very_pct = features.minutes_very_active / features.active_minutes_total
        intensity_score = min(very_pct * 20, 20)

    zone_score = min(features.active_zone_minutes / 30 * 10, 10)

    return round(steps_score + active_score + intensity_score + zone_score, 1)


def calculate_daily_calorie_burn(
    basal_metabolic_rate: float,
    activity_minutes: ActivityFeatures,
) -> float:
    """
    Estimate TDEE based on activity level.
    """
    activity_multiplier = 1.2

    if activity_minutes.active_minutes_total >= 60:
        activity_multiplier = 1.55
    elif activity_minutes.active_minutes_total >= 30:
        activity_multiplier = 1.375

    return basal_metabolic_rate * activity_multiplier
