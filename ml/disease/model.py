# ─── AgriFlow AI — Disease Model Architecture ─────────────────────────────────
"""
Transfer learning model for crop disease classification.

Backbone: MobileNetV3-Small (default)
  - ImageNet pretrained
  - Classification head replaced for num_classes

Also supports: EfficientNet-B0, ConvNeXt-Tiny
"""
import json
import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path

from .config import CONFIG, DiseaseModelConfig


def build_model(config: DiseaseModelConfig) -> nn.Module:
    """
    Build the classification model with transfer learning.
    The backbone is frozen initially; the classification head is trainable.
    """
    backbone = config.backbone
    num_classes = config.num_classes
    pretrained = config.pretrained

    weights_arg = "DEFAULT" if pretrained else None

    if backbone == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=weights_arg)
        # Replace the classifier head
        in_features = model.classifier[0].in_features
        model.classifier = nn.Sequential(
            nn.Linear(in_features, 256),
            nn.Hardswish(),
            nn.Dropout(p=config.dropout),
            nn.Linear(256, num_classes),
        )

    elif backbone == "efficientnet_b0":
        model = models.efficientnet_b0(weights=weights_arg)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=config.dropout),
            nn.Linear(in_features, num_classes),
        )

    elif backbone == "convnext_tiny":
        model = models.convnext_tiny(weights=weights_arg)
        in_features = model.classifier[2].in_features
        model.classifier[2] = nn.Linear(in_features, num_classes)

    elif backbone == "resnet50":
        model = models.resnet50(weights=weights_arg)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)

    else:
        raise ValueError(f"Unsupported backbone: {backbone}. "
                         f"Choose: mobilenet_v3_small | efficientnet_b0 | convnext_tiny | resnet50")

    return model


def load_model_for_inference(config: DiseaseModelConfig) -> tuple[nn.Module, list[str], str]:
    """
    Load a saved model + class names for inference.

    Returns:
      (model, class_names, status)
      status: "LOADED" | "MODEL NOT TRAINED"
    """
    if not config.best_model_path.exists():
        return None, [], "MODEL NOT TRAINED"

    if not config.class_names_path.exists():
        return None, [], "MODEL NOT TRAINED — class_names.json missing"

    with open(config.class_names_path) as f:
        class_names = json.load(f)

    num_classes = len(class_names)
    model_config = DiseaseModelConfig(num_classes=num_classes)

    model = build_model(model_config)

    checkpoint = torch.load(config.best_model_path, map_location="cpu")
    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.eval()
    print(f"✅  Model loaded from {config.best_model_path}")
    return model, class_names, "LOADED"


def count_parameters(model: nn.Module) -> dict:
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {"total": total, "trainable": trainable, "frozen": total - trainable}
