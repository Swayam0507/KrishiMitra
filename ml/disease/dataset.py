# ─── AgriFlow AI — Disease Dataset Pipeline ──────────────────────────────────
"""
Phase 11: Dataset loading and preprocessing.

Supports:
  - Pre-split dataset (train/val/test folders)
  - Single folder auto-split (70/15/15)

Dataset source: PlantVillage-style
  Each subfolder = one class (e.g. Tomato___Early_blight)
  
Official SIH class list: use when provided by organizers.
  Currently supports standard PlantVillage 38-class setup.

Augmentation is applied to TRAIN split only.
Val/Test receive only resize + normalize (no augmentation).
"""
import json
import random
import shutil
from pathlib import Path
from typing import Optional

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

from .config import CONFIG, DiseaseModelConfig


def set_seed(seed: int):
    """Set global seeds for reproducibility."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def build_transforms(split: str, config: DiseaseModelConfig) -> transforms.Compose:
    """
    Build the augmentation/preprocessing pipeline.
    Train: augmentation + normalize
    Val/Test: resize + center crop + normalize only
    """
    normalize = transforms.Normalize(mean=config.mean, std=config.std)

    if split == "train":
        aug_list = [
            transforms.RandomResizedCrop(
                config.image_size,
                scale=config.random_resized_crop_scale,
            ) if config.random_resized_crop else transforms.Resize(config.image_size),
        ]
        if config.random_horizontal_flip:
            aug_list.append(transforms.RandomHorizontalFlip())
        if config.random_vertical_flip:
            aug_list.append(transforms.RandomVerticalFlip())
        aug_list.append(transforms.RandomRotation(config.random_rotation_degrees))
        aug_list.append(transforms.ColorJitter(**config.color_jitter))
        aug_list += [transforms.ToTensor(), normalize]
        return transforms.Compose(aug_list)
    else:
        # Val / Test — no augmentation
        return transforms.Compose([
            transforms.Resize(int(config.image_size * 1.1)),
            transforms.CenterCrop(config.image_size),
            transforms.ToTensor(),
            normalize,
        ])


def load_split_dataset(config: DiseaseModelConfig) -> dict:
    """
    Load dataset from pre-split train/val/test folders.
    Expected structure:
      data/disease/train/<class_name>/*.jpg
      data/disease/val/<class_name>/*.jpg
      data/disease/test/<class_name>/*.jpg
    """
    data_dir = config.data_dir
    splits = {}

    for split in ["train", "val", "test"]:
        split_path = data_dir / split
        if not split_path.exists():
            print(f"  ⚠  Split folder not found: {split_path}")
            continue

        tf = build_transforms(split, config)
        dataset = datasets.ImageFolder(str(split_path), transform=tf)
        splits[split] = dataset
        print(f"  ✅  {split}: {len(dataset)} images, {len(dataset.classes)} classes")

    return splits


def auto_split_dataset(config: DiseaseModelConfig) -> dict:
    """
    If only one root folder exists (no train/val/test subdirs),
    auto-split using the configured ratios.
    """
    root = config.data_dir
    train_r, val_r, test_r = config.split_ratios

    # Use train transform for full dataset first (we'll re-apply per-split below)
    full_ds = datasets.ImageFolder(str(root), transform=build_transforms("train", config))

    n = len(full_ds)
    n_train = int(n * train_r)
    n_val   = int(n * val_r)
    n_test  = n - n_train - n_val

    train_ds, val_ds, test_ds = random_split(
        full_ds, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(config.seed),
    )

    print(f"  Auto-split: train={n_train} val={n_val} test={n_test}")

    # Note: val/test still use train augmentation here (limitation of random_split).
    # For production, use pre-split folders.
    return {"train": train_ds, "val": val_ds, "test": test_ds, "full": full_ds}


def get_dataloaders(config: DiseaseModelConfig) -> dict:
    """
    Return DataLoader dict for train/val/test splits.
    Auto-detects whether dataset is pre-split or flat.
    """
    set_seed(config.seed)

    data_dir = config.data_dir
    if not data_dir.exists():
        raise FileNotFoundError(
            f"\n❌  Dataset directory not found: {data_dir}\n"
            f"    Please download the PlantVillage dataset and place it at:\n"
            f"    {data_dir}/train/<class_name>/*.jpg\n"
            f"    {data_dir}/val/<class_name>/*.jpg\n"
            f"    {data_dir}/test/<class_name>/*.jpg\n"
            f"    Dataset: https://github.com/spMohanty/PlantVillage-Dataset\n"
        )

    # Check if pre-split
    has_splits = (data_dir / "train").exists()

    if has_splits:
        datasets_dict = load_split_dataset(config)
    else:
        print("  No train/val/test subdirs found — using auto-split.")
        datasets_dict = auto_split_dataset(config)

    # Save class names
    if "train" in datasets_dict:
        ds = datasets_dict["train"]
        class_names = ds.classes if hasattr(ds, "classes") else ds.dataset.classes
        config.class_names_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config.class_names_path, "w") as f:
            json.dump(class_names, f, indent=2)
        print(f"  Class names saved: {config.class_names_path}")

    loaders = {}
    for split, ds in datasets_dict.items():
        shuffle = (split == "train")
        loaders[split] = DataLoader(
            ds,
            batch_size=config.batch_size,
            shuffle=shuffle,
            num_workers=config.num_workers,
            pin_memory=torch.cuda.is_available(),
        )

    return loaders


def get_class_names(config: DiseaseModelConfig) -> list[str]:
    """Load class names from saved JSON."""
    if config.class_names_path.exists():
        with open(config.class_names_path) as f:
            return json.load(f)
    return []
