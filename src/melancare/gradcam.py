"""Grad-CAM (Selvaraju et al., ICCV 2017) and measures of whether it falls on the lesion."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


class GradCAM:
    """Weights the target layer's feature maps by the gradient of the class score.

    The result is a coarse heatmap (7x7 for these models, upsampled to the image size)
    of the regions that most increased the score for the chosen class.
    """

    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self._activations: torch.Tensor | None = None
        self._gradients: torch.Tensor | None = None
        self._handle = target_layer.register_forward_hook(self._save)

    def _save(self, _module, _inputs, output: torch.Tensor) -> None:
        self._activations = output
        output.register_hook(lambda grad: setattr(self, "_gradients", grad))

    def remove(self) -> None:
        self._handle.remove()

    def __call__(
        self, x: torch.Tensor, class_idx: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Return (cams of shape B x H x W scaled to [0, 1], logits of shape B x C).

        If `class_idx` is None, each image is explained for its predicted class.
        """
        self.model.eval()
        with torch.enable_grad():
            logits = self.model(x)
            if class_idx is None:
                class_idx = logits.argmax(1)
            self.model.zero_grad(set_to_none=True)
            logits.gather(1, class_idx.view(-1, 1).to(logits.device)).sum().backward()

        weights = self._gradients.mean(dim=(2, 3), keepdim=True)
        cam = F.relu((weights * self._activations).sum(1, keepdim=True))
        cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
        cam = cam.squeeze(1)
        lo = cam.amin(dim=(1, 2), keepdim=True)
        hi = cam.amax(dim=(1, 2), keepdim=True)
        cam = (cam - lo) / (hi - lo).clamp_min(1e-8)
        return cam.detach(), logits.detach()


def lesion_focus(cam: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    """How much of the heatmap falls on the lesion.

    energy_in_lesion: share of total heatmap mass inside the lesion mask. Easy to read, but
        depends on lesion size, and the coarse 7x7 heatmap always spills past the border.
    lesion_area: share of the image the lesion covers.
    focus_ratio: mean heat inside the lesion / mean heat outside it. 1 means the lesion gets
        no more attention than the surrounding skin; > 1 means attention is on the lesion.
        Comparable across small and large lesions.
    peak_in_lesion: whether the single hottest pixel is inside the lesion ("pointing game").
    """
    mask = mask.astype(bool)
    inside, outside = cam[mask], cam[~mask]
    total = cam.sum()
    peak = np.unravel_index(np.argmax(cam), cam.shape)
    if inside.size and outside.size:
        focus_ratio = float(inside.mean() / max(outside.mean(), 1e-6))
    else:
        focus_ratio = float("nan")  # lesion fills the whole crop, or is absent from it
    return {
        "energy_in_lesion": float(inside.sum() / total) if total > 0 else float("nan"),
        "lesion_area": float(mask.mean()),
        "focus_ratio": focus_ratio,
        "peak_in_lesion": bool(mask[peak]),
    }
