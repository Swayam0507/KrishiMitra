# ─── AgriFlow AI — Grad-CAM Explainability (Phase 17) ────────────────────────
"""
Grad-CAM: Gradient-weighted Class Activation Mapping.
Highlights the regions of the image that most influenced the model's prediction.

Reference: Selvaraju et al. (2017) "Grad-CAM: Visual Explanations from Deep Networks"

Usage:
  from disease.gradcam import GradCAM, generate_heatmap
  cam = generate_heatmap(model, image_path, pred_class_idx, config)
  # cam is saved to disk and the path returned
"""
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from typing import Optional


class GradCAM:
    """
    Grad-CAM implementation for CNN models.
    Works with MobileNetV3, EfficientNet, ConvNeXt, ResNet.
    """

    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients: Optional[torch.Tensor] = None
        self.activations: Optional[torch.Tensor] = None
        self._register_hooks()

    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_in, grad_out):
            self.gradients = grad_out[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(self, input_tensor: torch.Tensor, target_class: int) -> np.ndarray:
        """
        Generate a normalized Grad-CAM heatmap for a given class.
        Returns float32 array in [0, 1], shape (H, W).
        """
        self.model.eval()
        output = self.model(input_tensor)

        self.model.zero_grad()
        one_hot = torch.zeros_like(output)
        one_hot[0][target_class] = 1.0
        output.backward(gradient=one_hot)

        gradients  = self.gradients[0]    # (C, H, W)
        activations = self.activations[0]  # (C, H, W)

        # Global average pooling of gradients
        weights = gradients.mean(dim=(1, 2), keepdim=True)  # (C, 1, 1)
        cam = (weights * activations).sum(dim=0)             # (H, W)
        cam = torch.relu(cam)

        # Normalize to [0, 1]
        cam = cam.numpy()
        if cam.max() > cam.min():
            cam = (cam - cam.min()) / (cam.max() - cam.min())

        return cam.astype(np.float32)


def _get_target_layer(model: nn.Module, backbone: str) -> Optional[nn.Module]:
    """Return the last convolutional layer for the given backbone."""
    try:
        if backbone == "mobilenet_v3_small":
            return model.features[-1][0]
        elif backbone == "efficientnet_b0":
            return model.features[-1][0]
        elif backbone == "convnext_tiny":
            return model.features[-1][-1].block[0]
        elif backbone == "resnet50":
            return model.layer4[-1].conv3
        else:
            # Fallback: try to find the last Conv2d
            last_conv = None
            for module in model.modules():
                if isinstance(module, nn.Conv2d):
                    last_conv = module
            return last_conv
    except (AttributeError, IndexError):
        return None


def generate_heatmap(
    model: nn.Module,
    image_path: str,
    pred_class_idx: int,
    config,
    output_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Generate a Grad-CAM heatmap and save it as an overlay image.

    Returns the path to the saved heatmap image, or None if generation failed.
    """
    try:
        from PIL import Image
        import torchvision.transforms as T
        from disease.dataset import build_transforms

        path = Path(image_path)
        if not path.exists():
            return None

        # Load and preprocess image
        img_pil = Image.open(path).convert("RGB")
        tf = build_transforms("val", config)
        input_tensor = tf(img_pil).unsqueeze(0)

        # Get target layer
        target_layer = _get_target_layer(model, config.backbone)
        if target_layer is None:
            return None

        # Generate CAM
        cam_gen = GradCAM(model, target_layer)
        cam_array = cam_gen.generate_cam(input_tensor, pred_class_idx)

        # Resize CAM to original image size
        from PIL import Image as PILImage
        cam_img = PILImage.fromarray((cam_array * 255).astype(np.uint8)).convert("L")
        cam_img = cam_img.resize((config.image_size, config.image_size), PILImage.BILINEAR)

        # Create heatmap overlay
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))

        # Original
        img_resized = img_pil.resize((config.image_size, config.image_size))
        axes[0].imshow(img_resized)
        axes[0].set_title("Original Image")
        axes[0].axis("off")

        # Heatmap
        heatmap = np.array(cam_img) / 255.0
        axes[1].imshow(heatmap, cmap="jet")
        axes[1].set_title("Attention Heatmap")
        axes[1].axis("off")

        # Overlay
        axes[2].imshow(img_resized, alpha=0.7)
        axes[2].imshow(heatmap, cmap="jet", alpha=0.4)
        axes[2].set_title("Overlay\n(highlighted = model focus area)")
        axes[2].axis("off")

        fig.suptitle(
            "Grad-CAM Explanation — The highlighted region influenced the prediction.\n"
            "This is a visual explanation, not a diagnostic certainty.",
            fontsize=9,
        )
        plt.tight_layout()

        # Save
        out_dir = output_dir or Path("uploads/gradcam")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"gradcam_{path.stem}.png"
        plt.savefig(out_path, dpi=120)
        plt.close()

        return str(out_path)

    except Exception as e:
        print(f"  Grad-CAM generation failed: {e}")
        return None
