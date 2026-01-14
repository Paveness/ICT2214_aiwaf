import json
from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

DATA = Path("data/ai_requests.jsonl")
MODEL_OUT = Path("data/ai_model.joblib")

def load_rows():
    rows = []
    with DATA.open("r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            rows.append(obj["features"])
    return rows

def main():
    rows = load_rows()
    df = pd.DataFrame(rows).fillna(0)

    # Separate categoricals + numerics
    cat_cols = ["method"]
    num_cols = [c for c in df.columns if c not in cat_cols]

    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
            ("num", "passthrough", num_cols),
        ]
    )

    clf = IsolationForest(
        n_estimators=200,
        contamination=0.01,   # start low; adjust later
        random_state=42,
    )

    pipe = Pipeline([("pre", pre), ("clf", clf)])
    pipe.fit(df)

    MODEL_OUT.parent.mkdir(exist_ok=True)
    joblib.dump({"model": pipe, "columns": df.columns.tolist()}, MODEL_OUT)
    print("Saved:", MODEL_OUT)

if __name__ == "__main__":
    main()
