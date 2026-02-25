from pathlib import Path
from typing import Any, Optional

import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


class CircadiaModel:
    def __init__(
        self,
        model_type: str = "gradient_boosting",
        random_state: int = 42,
    ):
        self.model_type = model_type
        self.random_state = random_state
        self.model: Optional[Pipeline] = None
        self.feature_names: list[str] = []
        self.is_fitted = False

    def _create_pipeline(self) -> Pipeline:
        if self.model_type == "random_forest":
            regressor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=self.random_state,
            )
        elif self.model_type == "ridge":
            regressor = Ridge(alpha=1.0)
        else:
            regressor = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=self.random_state,
            )

        return Pipeline(
            [
                ("scaler", StandardScaler()),
                ("regressor", regressor),
            ]
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "CircadiaModel":
        self.model = self._create_pipeline()
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        return self.model.predict(X)

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> dict[str, float]:
        if self.model is None:
            self.model = self._create_pipeline()

        scores = cross_val_score(self.model, X, y, cv=cv, scoring="r2")
        return {
            "mean_r2": float(np.mean(scores)),
            "std_r2": float(np.std(scores)),
            "scores": scores.tolist(),
        }

    def save(self, path: Path) -> None:
        import pickle

        if not self.is_fitted:
            raise ValueError("Model not fitted. Cannot save.")

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    def load(self, path: Path) -> "CircadiaModel":
        import pickle

        with open(path, "rb") as f:
            self.model = pickle.load(f)
        self.is_fitted = True
        return self


def get_default_features() -> list[str]:
    return [
        "resting_hr",
        "hrv_rmssd",
        "sleep_score",
        "steps",
        "active_minutes",
        "spo2_avg",
        "breathing_rate",
        "minutes_deep",
        "minutes_rem",
        "calories",
    ]
