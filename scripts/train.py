"""Fine-tune an ImageNet-pretrained CNN to classify HAM10000 dermoscopic images into 7 classes.

The checkpoint with the best validation balanced accuracy (mean per-class sensitivity)
is kept, so the model is not rewarded for simply predicting the majority class (naevus).

Example:
    python scripts/train.py --arch efficientnet_b0 --epochs 20
    python scripts/train.py --limit 300 --epochs 1      # quick smoke test
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler

from melancare.data import CLASSES, SkinLesionDataset, build_transforms
from melancare.engine import predict, train_one_epoch, warmup_cosine
from melancare.metrics import summary_metrics
from melancare.model import ARCHS, build_model, get_device
from melancare.plots import plot_training_curves


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--runs-dir", type=Path, default=Path("runs"))
    p.add_argument("--run-name", default=None, help="Defaults to <arch>_<imbalance>_<timestamp>.")
    p.add_argument("--arch", default="efficientnet_b0", choices=ARCHS)
    p.add_argument("--img-size", type=int, default=224)
    p.add_argument("--epochs", type=int, default=20)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--weight-decay", type=float, default=1e-2)
    p.add_argument(
        "--imbalance",
        choices=["weighted_loss", "sampler", "none"],
        default="weighted_loss",
        help="How to handle class imbalance: inverse-frequency loss weights, "
             "oversample rare classes, or do nothing (useful as a comparison).",
    )
    p.add_argument("--patience", type=int, default=6, help="Stop after this many epochs without improvement.")
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, default=None, help="Use only N train and N val images (smoke test).")
    p.add_argument("--device", default=None, help="cpu, mps or cuda (auto-detected by default).")
    return p.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    device = get_device(args.device)
    run_name = args.run_name or f"{args.arch}_{args.imbalance}_{time.strftime('%Y%m%d-%H%M')}"
    run_dir = args.runs_dir / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    splits = pd.read_csv(args.data_dir / "splits.csv")
    train_df = splits[splits["split"] == "train"]
    val_df = splits[splits["split"] == "val"]
    if args.limit:
        train_df = train_df.sample(min(args.limit, len(train_df)), random_state=args.seed)
        val_df = val_df.sample(min(args.limit, len(val_df)), random_state=args.seed)

    image_dir = args.data_dir / "images"
    train_ds = SkinLesionDataset(train_df, image_dir, build_transforms(args.img_size, train=True))
    val_ds = SkinLesionDataset(val_df, image_dir, build_transforms(args.img_size, train=False))

    labels = np.array(train_ds.labels)
    counts = np.bincount(labels, minlength=len(CLASSES)).clip(min=1)
    print(f"Device: {device} | train {len(train_ds)} | val {len(val_ds)}")
    print("Training images per class:", dict(zip(CLASSES, counts.tolist())))

    loader_kw = dict(num_workers=args.num_workers, persistent_workers=args.num_workers > 0)
    sampler = None
    class_weights = None
    if args.imbalance == "weighted_loss":
        # "Balanced" weights: each class contributes equally to the loss in total.
        class_weights = torch.tensor(len(labels) / (len(CLASSES) * counts), dtype=torch.float32)
    elif args.imbalance == "sampler":
        sampler = WeightedRandomSampler(1.0 / counts[labels], num_samples=len(labels), replacement=True)

    train_loader = DataLoader(train_ds, args.batch_size, shuffle=sampler is None, sampler=sampler,
                              drop_last=True, **loader_kw)
    val_loader = DataLoader(val_ds, args.batch_size * 2, shuffle=False, **loader_kw)

    model = build_model(args.arch, len(CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(device) if class_weights is not None else None)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    steps = args.epochs * len(train_loader)
    scheduler = warmup_cosine(optimizer, warmup_steps=len(train_loader), total_steps=steps)

    config = {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()}
    config.update(run_name=run_name, device=str(device), train_images=len(train_ds), val_images=len(val_ds))
    (run_dir / "config.json").write_text(json.dumps(config, indent=2))

    history, best, stale = [], -1.0, 0
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scheduler, device)
        probs, y = predict(model, val_loader, device)
        m = summary_metrics(y, probs)
        val_loss = float(-np.log(probs[np.arange(len(y)), y].clip(1e-12)).mean())
        history.append({"epoch": epoch, "train_loss": train_loss, "val_loss": val_loss,
                        **{f"val_{k}": v for k, v in m.items()}, "seconds": time.time() - t0})
        print(f"Epoch {epoch:2d}/{args.epochs} | train loss {train_loss:.3f} | val loss {val_loss:.3f} | "
              f"bal acc {m['balanced_accuracy']:.3f} | macro AUC {m['macro_auc']:.3f} | "
              f"macro F1 {m['macro_f1']:.3f} | {time.time() - t0:.0f}s")

        if m["balanced_accuracy"] > best:
            best, stale = m["balanced_accuracy"], 0
            torch.save({"model": model.state_dict(), "arch": args.arch, "classes": CLASSES,
                        "img_size": args.img_size, "epoch": epoch, "val_metrics": m}, run_dir / "best.pt")
        else:
            stale += 1
            if stale >= args.patience:
                print(f"No improvement for {args.patience} epochs; stopping early.")
                break

    history_df = pd.DataFrame(history)
    history_df.to_csv(run_dir / "history.csv", index=False)
    plot_training_curves(history_df, run_dir / "training_curves.png")
    print(f"\nBest validation balanced accuracy: {best:.3f}. Saved to {run_dir}/best.pt")
    print(f"Next: python scripts/evaluate.py --run {run_dir}")


if __name__ == "__main__":
    main()
