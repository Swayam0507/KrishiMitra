# ─── AgriFlow AI — Disease Model Evaluation ───────────────────────────────────
"""
Phase 13: Complete model evaluation.

Primary SIH metric: Macro-F1 (NOT accuracy)
Also reports: accuracy, weighted-F1, per-class precision/recall/F1

Usage:
  cd KrishiMitra/ml
  python -m disease.evaluate

Saves reports to:
  reports/evaluation_results.json
  reports/confusion_matrix.png
  reports/per_class_metrics.csv

⚠  Reports reflect LOCAL test set results.
   Official SIH held-out field evaluation is separate.
"""
import json
import csv
import torch
import numpy as np
from pathlib import Path
from datetime import datetime

from .config import CONFIG, DiseaseModelConfig
from .dataset import get_dataloaders, build_transforms, set_seed, get_class_names
from .model import load_model_for_inference, build_model


def evaluate(config: DiseaseModelConfig = CONFIG) -> dict:
    print("\n" + "=" * 60)
    print("  AgriFlow AI — Disease Model Evaluation")
    print("=" * 60)

    set_seed(config.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ── Load model ────────────────────────────────────────────────────────────
    model, class_names, status = load_model_for_inference(config)
    if model is None:
        print(f"\n⚠  {status}")
        print("   Train the model first: python -m disease.train")
        return {"status": status, "results": None}

    model = model.to(device)

    # ── Load test data ────────────────────────────────────────────────────────
    try:
        loaders = get_dataloaders(config)
    except FileNotFoundError as e:
        print(str(e))
        return {"status": "DATASET NOT FOUND", "results": None}

    if "test" not in loaders:
        test_loader = loaders.get("val")
        split_used = "val"
        print("  ⚠  No test split found — evaluating on val split.")
    else:
        test_loader = loaders["test"]
        split_used = "test"

    print(f"\n  Split: {split_used}  |  Samples: {len(test_loader.dataset)}")

    # ── Inference ─────────────────────────────────────────────────────────────
    all_preds = []
    all_labels = []

    model.eval()
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            preds = outputs.argmax(1).cpu().numpy()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.numpy().tolist())

    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)

    # ── Metrics ───────────────────────────────────────────────────────────────
    num_classes = len(class_names)
    correct = (all_preds == all_labels).sum()
    accuracy = correct / len(all_labels)

    # Per-class metrics
    per_class = {}
    for i, cls in enumerate(class_names):
        tp = ((all_preds == i) & (all_labels == i)).sum()
        fp = ((all_preds == i) & (all_labels != i)).sum()
        fn = ((all_preds != i) & (all_labels == i)).sum()
        tn = ((all_preds != i) & (all_labels != i)).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        support = int((all_labels == i).sum())

        per_class[cls] = {
            "precision": round(float(precision), 4),
            "recall":    round(float(recall),    4),
            "f1":        round(float(f1),        4),
            "support":   support,
        }

    # Macro averages (SIH primary metric)
    macro_precision = np.mean([v["precision"] for v in per_class.values()])
    macro_recall    = np.mean([v["recall"]    for v in per_class.values()])
    macro_f1        = np.mean([v["f1"]        for v in per_class.values()])

    # Weighted averages
    total = len(all_labels)
    weighted_f1 = sum(
        per_class[cls]["f1"] * per_class[cls]["support"] / total
        for cls in class_names
    )

    # Confusion matrix (flat)
    confusion = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(all_labels, all_preds):
        confusion[t][p] += 1

    results = {
        "split_evaluated": split_used,
        "num_samples": len(all_labels),
        "num_classes": num_classes,
        "accuracy":          round(float(accuracy),         4),
        "macro_f1":          round(float(macro_f1),         4),
        "macro_precision":   round(float(macro_precision),  4),
        "macro_recall":      round(float(macro_recall),     4),
        "weighted_f1":       round(float(weighted_f1),      4),
        "per_class_metrics": per_class,
        "confusion_matrix":  confusion.tolist(),
        "class_names":       class_names,
        "primary_metric":    "macro_f1",
        "evaluated_at":      datetime.now().isoformat(),
        "disclaimer": (
            "These metrics are from the LOCAL test/val set. "
            "Official SIH held-out field evaluation result: PENDING ORGANIZER EVALUATION."
        ),
    }

    # ── Print summary ─────────────────────────────────────────────────────────
    print(f"\n  ── Local {split_used} Results ────────────────────────")
    print(f"  Accuracy        : {accuracy:.4f}  ({correct}/{len(all_labels)})")
    print(f"  Macro-F1        : {macro_f1:.4f}  ← SIH PRIMARY METRIC")
    print(f"  Macro-Precision : {macro_precision:.4f}")
    print(f"  Macro-Recall    : {macro_recall:.4f}")
    print(f"  Weighted-F1     : {weighted_f1:.4f}")
    print(f"\n  ⚠  Official SIH held-out evaluation: PENDING ORGANIZER EVALUATION")
    print("  " + "=" * 54)

    # ── Save reports ──────────────────────────────────────────────────────────
    config.reports_dir.mkdir(parents=True, exist_ok=True)

    # JSON report
    report_path = config.reports_dir / "evaluation_results.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved: {report_path}")

    # CSV per-class
    csv_path = config.reports_dir / "per_class_metrics.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["class", "precision", "recall", "f1", "support"])
        for cls, m in per_class.items():
            writer.writerow([cls, m["precision"], m["recall"], m["f1"], m["support"]])
    print(f"  Per-class CSV:  {csv_path}")

    # Attempt confusion matrix plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(min(20, num_classes), min(16, num_classes)))
        im = ax.imshow(confusion, interpolation="nearest", cmap="Blues")
        ax.set_title(f"Confusion Matrix — {split_used} split\nMacro-F1: {macro_f1:.4f}")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        if num_classes <= 20:
            ax.set_xticks(range(num_classes))
            ax.set_yticks(range(num_classes))
            ax.set_xticklabels(class_names, rotation=90, fontsize=7)
            ax.set_yticklabels(class_names, fontsize=7)
        plt.colorbar(im, ax=ax)
        plt.tight_layout()
        cm_path = config.reports_dir / "confusion_matrix.png"
        plt.savefig(cm_path, dpi=150)
        plt.close()
        print(f"  Confusion matrix: {cm_path}")
    except ImportError:
        print("  (matplotlib not installed — confusion matrix image skipped)")

    return {"status": "OK", "results": results}


if __name__ == "__main__":
    evaluate()
