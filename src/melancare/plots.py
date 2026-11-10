"""Figures for training curves, evaluation and Grad-CAM."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import confusion_matrix, roc_curve  # noqa: E402


def _save(fig, path: Path, rect=(0, 0, 1, 1)) -> None:
    fig.tight_layout(rect=rect)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_training_curves(history: pd.DataFrame, path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.plot(history["epoch"], history["train_loss"], label="train (weighted)")
    ax1.plot(history["epoch"], history["val_loss"], label="validation")
    ax1.set(xlabel="Epoch", ylabel="Cross-entropy loss", title="Loss")
    ax1.legend()
    for col in ["val_balanced_accuracy", "val_macro_auc", "val_macro_f1"]:
        ax2.plot(history["epoch"], history[col], label=col.removeprefix("val_").replace("_", " "))
    ax2.set(xlabel="Epoch", ylabel="Score", title="Validation metrics", ylim=(0, 1))
    ax2.legend()
    _save(fig, path)


def plot_confusion_matrix(y_true, y_pred, classes: list[str], path: Path, title: str) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=range(len(classes)))
    row_pct = cm / cm.sum(1, keepdims=True).clip(min=1)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(row_pct, cmap="Blues", vmin=0, vmax=1)
    for i in range(len(classes)):
        for j in range(len(classes)):
            colour = "white" if row_pct[i, j] > 0.5 else "black"
            ax.text(j, i, f"{row_pct[i, j]:.0%}\n({cm[i, j]})", ha="center", va="center",
                    fontsize=8, color=colour)
    ax.set(xticks=range(len(classes)), yticks=range(len(classes)),
           xticklabels=classes, yticklabels=classes,
           xlabel="Predicted", ylabel="True diagnosis", title=title)
    _save(fig, path)


def plot_roc_curves(y_true, probs, classes: list[str], path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(6, 6))
    for k, name in enumerate(classes):
        t = y_true == k
        if t.any() and (~t).any():
            fpr, tpr, _ = roc_curve(t, probs[:, k])
            ax.plot(fpr, tpr, label=name)
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set(xlabel="1 - specificity", ylabel="Sensitivity", title=title)
    ax.legend(loc="lower right")
    _save(fig, path)


def plot_binary_roc(y_bin, score, op: dict, path: Path, title: str) -> None:
    fpr, tpr, _ = roc_curve(y_bin, score)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(fpr, tpr, label=f"AUC {op['auc']:.3f}")
    ax.scatter([1 - op["specificity"]], [op["sensitivity"]], color="red", zorder=3,
               label=f"Threshold from validation\n(sens {op['sensitivity']:.2f}, spec {op['specificity']:.2f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set(xlabel="1 - specificity", ylabel="Sensitivity", title=title)
    ax.legend(loc="lower right", fontsize=8)
    _save(fig, path)


def plot_gradcam_grid(items: list[dict], path: Path, title: str, per_row: int = 2) -> None:
    """Each item: image (HxWx3), cam (HxW), mask (HxW bool), caption. Shows image + overlay pairs."""
    if not items:
        return
    rows = int(np.ceil(len(items) / per_row))
    fig, axes = plt.subplots(rows, 2 * per_row, figsize=(3.2 * 2 * per_row, 3.4 * rows), squeeze=False)
    for ax in axes.flat:
        ax.axis("off")
    for i, item in enumerate(items):
        ax_img, ax_cam = axes[i // per_row, 2 * (i % per_row)], axes[i // per_row, 2 * (i % per_row) + 1]
        ax_img.imshow(item["image"])
        ax_img.set_title(item["caption"], fontsize=8)
        ax_cam.imshow(item["image"])
        ax_cam.imshow(item["cam"], cmap="jet", alpha=0.45, vmin=0, vmax=1)
        if item.get("mask") is not None and item["mask"].any():
            ax_cam.contour(item["mask"], levels=[0.5], colors="white", linewidths=1)
        ax_cam.set_title(item.get("cam_caption", "Grad-CAM (white = lesion border)"), fontsize=8)
    fig.suptitle(title, fontsize=13)
    _save(fig, path, rect=(0, 0, 1, 1 - 0.35 / (3.4 * rows)))
