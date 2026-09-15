# ─── AgriFlow AI — Disease Model Training ─────────────────────────────────────
"""
Phase 12: Complete training pipeline.

Usage:
  cd KrishiMitra/ml
  python -m disease.train

Requirements:
  Dataset must be at: ml/data/disease/train/<class>/*.jpg
  Install:  pip install -r requirements.txt

Saves:
  ml/model/disease/best_model.pth
  ml/model/disease/class_names.json
  ml/model/disease/training_config.json
"""
import json
import time
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR, StepLR
from pathlib import Path

from .config import CONFIG, DiseaseModelConfig
from .dataset import get_dataloaders, set_seed
from .model import build_model, count_parameters


def train(config: DiseaseModelConfig = CONFIG):
    print("\n" + "=" * 60)
    print("  AgriFlow AI — Disease Model Training")
    print("=" * 60)
    print(f"  Backbone:      {config.backbone}")
    print(f"  Batch size:    {config.batch_size}")
    print(f"  Epochs:        {config.num_epochs}")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Seed:          {config.seed}")
    print(f"  Device:        {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print("=" * 60)

    set_seed(config.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # ── Dataset ───────────────────────────────────────────────────────────────
    try:
        loaders = get_dataloaders(config)
    except FileNotFoundError as e:
        print(str(e))
        return

    if "train" not in loaders or "val" not in loaders:
        print("❌  train and val splits are required. Aborting.")
        return

    train_loader = loaders["train"]
    val_loader   = loaders["val"]

    # Update num_classes from actual dataset
    train_ds = train_loader.dataset
    if hasattr(train_ds, "classes"):
        num_classes = len(train_ds.classes)
    elif hasattr(train_ds, "dataset") and hasattr(train_ds.dataset, "classes"):
        num_classes = len(train_ds.dataset.classes)
    else:
        num_classes = config.num_classes

    config.num_classes = num_classes
    print(f"\n  Classes: {num_classes}")
    print(f"  Train samples: {len(train_loader.dataset)}")
    print(f"  Val samples:   {len(val_loader.dataset)}\n")

    # ── Model ─────────────────────────────────────────────────────────────────
    model = build_model(config).to(device)
    params = count_parameters(model)
    print(f"  Parameters: {params['total']:,} total, {params['trainable']:,} trainable\n")

    # ── Loss + Optimizer ──────────────────────────────────────────────────────
    criterion = nn.CrossEntropyLoss()

    if config.optimizer == "adam":
        optimizer = optim.Adam(
            model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
        )
    else:
        optimizer = optim.SGD(
            model.parameters(), lr=config.learning_rate,
            momentum=config.momentum, weight_decay=config.weight_decay
        )

    if config.scheduler == "cosine":
        scheduler = CosineAnnealingLR(optimizer, T_max=config.num_epochs, eta_min=1e-6)
    elif config.scheduler == "step":
        scheduler = StepLR(optimizer, step_size=config.step_size, gamma=config.gamma)
    else:
        scheduler = None

    # ── Training loop ─────────────────────────────────────────────────────────
    best_val_acc  = 0.0
    best_model_wts = copy.deepcopy(model.state_dict())
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    for epoch in range(1, config.num_epochs + 1):
        t0 = time.time()

        # ─ Train phase ────────────────────────────────────────────────────────
        model.train()
        running_loss = 0.0
        running_correct = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss    += loss.item() * inputs.size(0)
            running_correct += (outputs.argmax(1) == labels).sum().item()

        train_loss = running_loss / len(train_loader.dataset)
        train_acc  = running_correct / len(train_loader.dataset)

        # ─ Validation phase ───────────────────────────────────────────────────
        model.eval()
        val_loss = 0.0
        val_correct = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss    += loss.item() * inputs.size(0)
                val_correct += (outputs.argmax(1) == labels).sum().item()

        val_loss /= len(val_loader.dataset)
        val_acc   = val_correct / len(val_loader.dataset)

        if scheduler:
            scheduler.step()

        # ─ Log ────────────────────────────────────────────────────────────────
        elapsed = time.time() - t0
        history["train_loss"].append(round(train_loss, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["train_acc"].append(round(train_acc, 4))
        history["val_acc"].append(round(val_acc, 4))

        print(
            f"  Epoch {epoch:>3}/{config.num_epochs}  "
            f"train_loss={train_loss:.4f}  train_acc={train_acc:.4f}  "
            f"val_loss={val_loss:.4f}  val_acc={val_acc:.4f}  "
            f"({elapsed:.1f}s)"
        )

        # ─ Best model ─────────────────────────────────────────────────────────
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            patience_counter = 0
            print(f"    ✅  New best val_acc = {best_val_acc:.4f}")
        else:
            patience_counter += 1

        # ─ Early stopping ─────────────────────────────────────────────────────
        if config.early_stopping and patience_counter >= config.patience:
            print(f"\n  Early stopping at epoch {epoch} (patience={config.patience})")
            break

    # ── Save ──────────────────────────────────────────────────────────────────
    config.model_dir.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state_dict": best_model_wts,
            "val_acc": best_val_acc,
            "epoch": epoch,
            "backbone": config.backbone,
            "num_classes": config.num_classes,
        },
        config.best_model_path,
    )
    print(f"\n  ✅  Best model saved: {config.best_model_path}")
    print(f"  Best val_acc = {best_val_acc:.4f}")

    # Save training config
    cfg_dict = {
        "backbone": config.backbone,
        "num_classes": config.num_classes,
        "image_size": config.image_size,
        "batch_size": config.batch_size,
        "num_epochs": epoch,
        "learning_rate": config.learning_rate,
        "optimizer": config.optimizer,
        "scheduler": config.scheduler,
        "seed": config.seed,
        "best_val_acc": best_val_acc,
        "history": history,
        "disclaimer": "Reported on LOCAL validation set. Official SIH held-out evaluation is separate.",
    }
    with open(config.config_save_path, "w") as f:
        json.dump(cfg_dict, f, indent=2)
    print(f"  Training config saved: {config.config_save_path}")

    return {"best_val_acc": best_val_acc, "history": history}


if __name__ == "__main__":
    train()
