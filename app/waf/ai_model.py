from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("data/ai_model.joblib")

class AIAnomalyScorer:
    def __init__(self):
        self.bundle = None

    def is_ready(self) -> bool:
        return self.bundle is not None

    def load(self):
        if MODEL_PATH.exists():
            self.bundle = joblib.load(MODEL_PATH)

    def score(self, features: dict) -> float:
        """
        Return anomaly score in [0,1] (higher = more anomalous).
        """
        if not self.bundle:
            return 0.0

        model = self.bundle["model"]
        cols = self.bundle["columns"]

        df = pd.DataFrame([features])
        # align columns (missing -> 0)
        for c in cols:
            if c not in df.columns:
                df[c] = 0
        df = df[cols].fillna(0)

        # IsolationForest: decision_function higher = more normal
        normality = model.decision_function(df)[0]  # roughly ~[-0.5, 0.5] depending
        # convert to 0..1 anomaly-ish
        # (simple monotonic mapping; tune later)
        anomaly = 1.0 / (1.0 + (2.71828 ** (normality * 5.0)))
        return float(anomaly)
