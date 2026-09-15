# ─── AgriFlow AI — Crop Recommendation ML (Phase 18) ─────────────────────────
"""
Train a Random Forest classifier for crop recommendation.

Dataset source: Crop Recommendation Dataset
  https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
  
Features: N, P, K, temperature, humidity, ph, rainfall
Target: crop name (22 classes)

SIH Bonus Module A — Crop Recommendation

Usage:
  cd KrishiMitra/ml
  python -m crop_recommendation.train
"""
import json
import pickle
import csv
import numpy as np
from pathlib import Path
from datetime import datetime

ML_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR  = ML_ROOT / "data" / "crop_recommendation"
MODEL_DIR = ML_ROOT / "model" / "crop_recommendation"
REPORTS_DIR = ML_ROOT.parent / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH   = MODEL_DIR / "crop_recommender.pkl"
SCALER_PATH  = MODEL_DIR / "scaler.pkl"
CLASSES_PATH = MODEL_DIR / "classes.json"
CONFIG_PATH  = MODEL_DIR / "config.json"

RANDOM_STATE = 42
TEST_SIZE    = 0.20
VAL_SIZE     = 0.15

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN   = "label"


def train():
    print("\n" + "=" * 60)
    print("  AgriFlow AI — Crop Recommendation Model Training")
    print("=" * 60)

    # ── Check for dataset ─────────────────────────────────────────────────────
    dataset_path = DATA_DIR / "Crop_recommendation.csv"
    if not dataset_path.exists():
        alt_path = DATA_DIR / "crop_recommendation.csv"
        if alt_path.exists():
            dataset_path = alt_path
        else:
            print(f"\n❌  Dataset not found at: {dataset_path}")
            print(f"    Download from Kaggle:")
            print(f"    https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset")
            print(f"    Place the CSV at: {dataset_path}")
            return

    try:
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import (
            accuracy_score, f1_score, precision_score, recall_score,
            classification_report,
        )
    except ImportError as e:
        print(f"\n❌  Missing dependency: {e}")
        print("    Install: pip install scikit-learn pandas")
        return

    # ── Load data ─────────────────────────────────────────────────────────────
    df = pd.read_csv(dataset_path)
    print(f"\n  Dataset: {len(df)} samples, {df[TARGET_COLUMN].nunique()} crops")
    print(f"  Crops: {sorted(df[TARGET_COLUMN].unique().tolist())}")

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    # ── Train/val/test split ──────────────────────────────────────────────────
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval,
        test_size=VAL_SIZE / (1 - TEST_SIZE),
        random_state=RANDOM_STATE,
        stratify=y_trainval,
    )
    print(f"  Split: train={len(X_train)} val={len(X_val)} test={len(X_test)}")

    # ── Preprocessing ─────────────────────────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s   = scaler.transform(X_val)
    X_test_s  = scaler.transform(X_test)

    # ── Model: Random Forest ───────────────────────────────────────────────────
    # Random Forest chosen for:
    #   - Good accuracy on tabular data
    #   - Feature importance available (explainable)
    #   - Robust to overfitting
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    print(f"\n  Training Random Forest (n_estimators=200)...")
    model.fit(X_train_s, y_train)

    # ── Evaluation ────────────────────────────────────────────────────────────
    def evaluate_split(X, y, name):
        y_pred = model.predict(X)
        acc  = accuracy_score(y, y_pred)
        f1   = f1_score(y, y_pred, average="macro", zero_division=0)
        prec = precision_score(y, y_pred, average="macro", zero_division=0)
        rec  = recall_score(y, y_pred, average="macro", zero_division=0)
        print(f"  {name}: acc={acc:.4f} macro-F1={f1:.4f} precision={prec:.4f} recall={rec:.4f}")
        return {"accuracy": round(acc, 4), "macro_f1": round(f1, 4),
                "precision": round(prec, 4), "recall": round(rec, 4)}

    print()
    val_metrics  = evaluate_split(X_val_s, y_val, "Val ")
    test_metrics = evaluate_split(X_test_s, y_test, "Test")

    # ── Feature importance ────────────────────────────────────────────────────
    importances = dict(zip(FEATURE_COLUMNS, model.feature_importances_.round(4).tolist()))
    print(f"\n  Feature importances: {importances}")

    # ── Save model ────────────────────────────────────────────────────────────
    classes = sorted(list(set(y)))
    with open(MODEL_PATH,  "wb") as f: pickle.dump(model,  f)
    with open(SCALER_PATH, "wb") as f: pickle.dump(scaler, f)
    with open(CLASSES_PATH, "w") as f: json.dump(classes, f, indent=2)

    config_data = {
        "model": "RandomForest",
        "n_estimators": 200,
        "max_depth": 15,
        "random_state": RANDOM_STATE,
        "features": FEATURE_COLUMNS,
        "num_classes": len(classes),
        "dataset": "Crop Recommendation Dataset (Kaggle/Atharva Ingle)",
        "split": {"train": len(X_train), "val": len(X_val), "test": len(X_test)},
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "feature_importances": importances,
        "trained_at": datetime.now().isoformat(),
        "disclaimer": "Metrics are from local test set. Not from SIH held-out evaluation.",
    }
    with open(CONFIG_PATH, "w") as f: json.dump(config_data, f, indent=2)

    print(f"\n  ✅  Model saved: {MODEL_PATH}")
    print(f"  ✅  Classes saved: {CLASSES_PATH}")


if __name__ == "__main__":
    train()
