import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np

from ..storage import DuckDBStorage
from .model import CircadiaModel

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, storage: DuckDBStorage, model_path: Path):
        self.storage = storage
        self.model_path = model_path
        self.model: Optional[CircadiaModel] = None

    def load_model(self) -> CircadiaModel:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")

        model = CircadiaModel()
        model.load(self.model_path)
        self.model = model
        return model

    def predict_next_day(self) -> dict[str, Any]:
        if self.model is None:
            self.load_model()

        query = """
        SELECT
            r.date,
            r.value as resting_hr,
            h.daily_rmssd as hrv_rmssd,
            s.efficiency as sleep_efficiency,
            s.minutes_asleep,
            s.minutes_deep,
            s.minutes_rem,
            a.steps,
            a.active_minutes_total as active_minutes,
            a.calories,
            sp.avg as spo2_avg,
            b.value as breathing_rate
        FROM resting_hr r
        LEFT JOIN hrv h ON r.date = h.date AND r.device = h.device
        LEFT JOIN sleep_summary s ON r.date = s.date AND r.device = s.device
        LEFT JOIN daily_summary a ON r.date = a.date AND r.device = a.device
        LEFT JOIN spo2 sp ON r.date = sp.date AND r.device = sp.device
        LEFT JOIN breathing_rate b ON r.date = b.date AND r.device = b.device
        ORDER BY r.date DESC
        LIMIT 1
        """

        df = self.storage.execute(query).df()

        if df.empty:
            raise ValueError("No recent data found for prediction")

        features = [
            df["resting_hr"].iloc[0] or 60,
            df["hrv_rmssd"].iloc[0] or 30,
            df["sleep_efficiency"].iloc[0] or 85,
            df["steps"].iloc[0] or 5000,
            df["active_minutes"].iloc[0] or 20,
            df["spo2_avg"].iloc[0] or 97,
            df["breathing_rate"].iloc[0] or 14,
            df["minutes_deep"].iloc[0] or 60,
            df["minutes_rem"].iloc[0] or 90,
            df["calories"].iloc[0] or 2000,
        ]

        X = np.array([features])
        prediction = self.model.predict(X)[0]

        return {
            "prediction": float(prediction),
            "date": str(df["date"].iloc[0]),
            "features": dict(zip(self.model.feature_names, features)),
        }

    def predict_range(self, days: int = 7) -> list[dict[str, Any]]:
        predictions = []
        for _ in range(days):
            try:
                pred = self.predict_next_day()
                predictions.append(pred)
            except Exception as e:
                logger.warning(f"Prediction failed: {e}")
                break

        return predictions
