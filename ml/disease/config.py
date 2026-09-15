# ─── AgriFlow AI — Disease Model Configuration ────────────────────────────────
"""
Reproducible training configuration.
All settings documented for SIH submission.

Random seed: 42 (set everywhere for reproducibility)
"""
from dataclasses import dataclass, field
from pathlib import Path

# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_ROOT      = Path(__file__).resolve().parent.parent
DATA_DIR     = ML_ROOT / "data" / "disease"
MODEL_DIR    = ML_ROOT / "model" / "disease"
REPORTS_DIR  = ML_ROOT.parent / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DiseaseModelConfig:
    # ── Reproducibility ────────────────────────────────────────────────────────
    seed: int = 42

    # ── Dataset ───────────────────────────────────────────────────────────────
    data_dir: Path = DATA_DIR
    # Expected structure: data/disease/{split}/{class_name}/image.jpg
    # Supported splits: train / val / test
    # Source: PlantVillage-style dataset
    # Reference: https://github.com/spMohanty/PlantVillage-Dataset
    train_split: str = "train"
    val_split:   str = "val"
    test_split:  str = "test"
    # Train/val/test split ratio (if splitting from a single folder)
    split_ratios: tuple = (0.70, 0.15, 0.15)

    # ── Model architecture ─────────────────────────────────────────────────────
    # MobileNetV3-Small — chosen for:
    #   - Small size (~2.5 MB)
    #   - Efficient on CPU/student hardware
    #   - Strong accuracy on PlantVillage benchmarks
    #   - Available in torchvision without extra install
    backbone: str = "mobilenet_v3_small"   # or "efficientnet_b0" / "convnext_tiny"
    pretrained: bool = True                # ImageNet pretrained weights
    num_classes: int = 38                  # PlantVillage has 38 classes (39 with background)
    dropout: float = 0.2

    # ── Image preprocessing ────────────────────────────────────────────────────
    image_size: int = 224      # Standard for MobileNet/EfficientNet
    mean: tuple = (0.485, 0.456, 0.406)   # ImageNet mean
    std:  tuple = (0.229, 0.224, 0.225)   # ImageNet std

    # ── Training augmentation (applied to train split only) ───────────────────
    # These augmentations match common PlantVillage preprocessing papers
    random_horizontal_flip: bool = True
    random_vertical_flip:   bool = True
    random_rotation_degrees: int = 20
    color_jitter: dict = field(default_factory=lambda: {
        "brightness": 0.3,
        "contrast":   0.3,
        "saturation": 0.2,
        "hue":        0.05,
    })
    random_resized_crop: bool = True
    random_resized_crop_scale: tuple = (0.7, 1.0)

    # ── Training hyperparameters ───────────────────────────────────────────────
    batch_size:    int   = 32
    num_epochs:    int   = 30
    learning_rate: float = 1e-3
    weight_decay:  float = 1e-4
    momentum:      float = 0.9      # used by SGD
    optimizer:     str   = "adam"   # "adam" or "sgd"
    scheduler:     str   = "cosine" # "cosine" | "step" | "none"
    step_size:     int   = 7        # for StepLR
    gamma:         float = 0.1      # for StepLR
    num_workers:   int   = 2        # DataLoader workers

    # ── Early stopping ─────────────────────────────────────────────────────────
    early_stopping: bool = True
    patience:       int  = 7        # epochs without val improvement

    # ── Output ────────────────────────────────────────────────────────────────
    model_dir: Path     = MODEL_DIR
    best_model_path: Path = MODEL_DIR / "best_model.pth"
    class_names_path: Path = MODEL_DIR / "class_names.json"
    config_save_path: Path = MODEL_DIR / "training_config.json"
    reports_dir: Path  = REPORTS_DIR

    # ── Primary metric ─────────────────────────────────────────────────────────
    # SIH ranking metric is Macro-F1 (not accuracy)
    primary_metric: str = "macro_f1"


# Singleton for import convenience
CONFIG = DiseaseModelConfig()
