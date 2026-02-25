import logging
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from ..storage import DuckDBStorage
from .model import CircadiaModel, get_default_features

logger = logging.getLogger(__name__)


class ModelTrainer:
    def __init__(self, storage: DuckDBStorage):
        self.storage = storage
        self.feature_names = get_default_features()

    def load_training_data(
        self,
        target: str = "sleep_score",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        query = f"""
        SELECT
            r.date,
            r.value as resting_hr,
            h.daily_rmssd as hrv_rmssd,
            s.efficiency as sleep_efficiency,
            s.minutes_asleep,
            s.minutes_deep,
            s.minutes_rem,
            s.minutes_light,
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
        """

        if start_date and end_date:
            query += f" WHERE r.date BETWEEN '{start_date}' AND '{end_date}'"
        elif start_date:
            query += f" WHERE r.date >= '{start_date}'"
        elif end_date:
            query += f" WHERE r.date <= '{end_date}'"

        df = self.storage.execute(query).df()

        if df.empty:
            raise ValueError("No training data found")

        if target == "sleep_score":
            y = df["minutes_asleep"].fillna(0)
        else:
            y = df[target].fillna(0)

        X = df[self.feature_names].fillna(0).values

        return X, y.values

    def train(
        self,
        target: str = "sleep_score",
        model_type: str = "gradient_boosting",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict[str, Any]:
        logger.info(f"Training model for {target}")

        X, y = self.load_training_data(target, start_date, end_date)

        model = CircadiaModel(model_type=model_type)

        cv_results = model.cross_validate(X, y)
        logger.info(
            f"Cross-validation R2: {cv_results['mean_r2']:.3f} (+/- {cv_results['std_r2']:.3f})"
        )

        model.fit(X, y)

        return {
            "target": target,
            "model": model,
            "cv_results": cv_results,
            "n_samples": len(y),
            "feature_names": self.feature_names,
        }

    def save_model(self, model: CircadiaModel, path: Path) -> None:
        model.save(path)
        logger.info(f"Model saved to {path}")
