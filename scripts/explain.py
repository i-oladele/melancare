"""Grad-CAM explanations, plus a measurement of whether the model attends to the lesion.

For each image in the chosen split, a Grad-CAM heatmap is computed for the predicted class
and compared with the expert lesion segmentation mask (Tschandl et al.):

    focus_ratio       mean heat inside the lesion / mean heat outside it
                      (1 = lesion gets no more attention than surrounding skin; > 1 = on the lesion)
    peak_in_lesion    whether the hottest point of the heatmap is inside the lesion
    energy_in_lesion  share of the heatmap inside the lesion (depends on lesion size)
    lesion_area       share of the image the lesion covers

Outputs in <run>/explain/: example figures, attention_stats.csv and summary.md.

Example:
    python scripts/explain.py --run runs/efficientnet_b0_weighted_loss_20261109-2100
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import DataLoader
from torchvision.transforms import InterpolationMode
from tqdm import tqdm

from melancare.data import SkinLesionDataset, build_transforms, eval_geometry
from melancare.gradcam import GradCAM, lesion_focus
from melancare.model import get_device, gradcam_layer, load_checkpoint
from melancare.plots import plot_gradcam_grid


def describe(g: pd.DataFrame) -> dict:
    return {
        "n": len(g),
        "median focus ratio": g["focus_ratio"].median(),
        "peak on lesion": g["peak_in_lesion"].mean(),
        "attention not on lesion": (g["focus_ratio"] <= 1).mean(),
        "mean heatmap share on lesion": g["energy_in_lesion"].mean(),
        "mean lesion area": g["lesion_area"].mean(),
    }


def md_table(df: pd.DataFrame, index_name: str) -> str:
    cols = [index_name, *df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for idx, row in df.iterrows():
        cells = [str(idx)] + [f"{v:.0f}" if k == "n" else f"{v:.2f}" for k, v in row.items()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--split", default="test", choices=["train", "val", "test"])
    p.add_argument("--target", default="pred", choices=["pred", "true"],
                   help="Explain the predicted class (default) or the true diagnosis.")
    p.add_argument("--n-per-class", type=int, default=2)
    p.add_argument("--n-gallery", type=int, default=8)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--num-workers", type=int, default=2)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--device", default=None)
    args = p.parse_args()

    device = get_device(args.device)
    model, ckpt = load_checkpoint(args.run, device)
    classes, size = ckpt["classes"], ckpt["img_size"]
    gradcam = GradCAM(model, gradcam_layer(model, ckpt["arch"]))
    out_dir = args.run / "explain"
    out_dir.mkdir(exist_ok=True)

    splits = pd.read_csv(args.data_dir / "splits.csv")
    df = splits[splits["split"] == args.split].reset_index(drop=True)
    ds = SkinLesionDataset(df, args.data_dir / "images", build_transforms(size, train=False))
    loader = DataLoader(ds, batch_size=args.batch_size, num_workers=args.num_workers)
    image_geom = eval_geometry(size)
    mask_geom = eval_geometry(size, InterpolationMode.NEAREST)
    mask_dir = args.data_dir / "masks"

    def load_mask(image_id: str) -> np.ndarray | None:
        path = mask_dir / f"{image_id}.png"
        if not path.exists():
            return None
        with Image.open(path) as m:
            return np.array(mask_geom(m.convert("L"))) > 127

    cams = np.zeros((len(ds), size, size), dtype=np.uint8)
    rows, start = [], 0
    for x, y in tqdm(loader, desc="Grad-CAM"):
        target = y if args.target == "true" else None
        cam, logits = gradcam(x.to(device), target)
        cam = cam.cpu().numpy()
        probs = torch.softmax(logits, 1).cpu().numpy()
        for j in range(len(y)):
            i = start + j
            cams[i] = (cam[j] * 255).round().astype(np.uint8)
            row = {"image_id": df.at[i, "image_id"], "dx": classes[int(y[j])],
                   "pred_dx": classes[probs[j].argmax()], "confidence": float(probs[j].max())}
            row["correct"] = row["dx"] == row["pred_dx"]
            mask = load_mask(row["image_id"])
            if mask is not None:
                row.update(lesion_focus(cam[j], mask))
            rows.append(row)
        start += len(y)

    stats = pd.DataFrame(rows)
    stats.to_csv(out_dir / "attention_stats.csv", index=False)

    # --- Figures ---
    rng = np.random.default_rng(args.seed)

    def item(i: int) -> dict:
        r = stats.iloc[i]
        image = np.asarray(image_geom(ds.load_image(i))) / 255.0
        mask = load_mask(r["image_id"])
        focus = f"focus ratio {r['focus_ratio']:.1f}" if "focus_ratio" in r else ""
        return {"image": image, "cam": cams[i] / 255.0, "mask": mask,
                "caption": f"{r['image_id']}\ntrue {r['dx']} | pred {r['pred_dx']} ({r['confidence']:.0%})",
                "cam_caption": focus}

    by_class = []
    for c in classes:
        idx = np.flatnonzero((stats["dx"] == c) & stats["correct"])
        by_class += [item(i) for i in rng.choice(idx, min(args.n_per_class, len(idx)), replace=False)]
    plot_gradcam_grid(by_class, out_dir / "gradcam_correct_by_class.png",
                      "Correct predictions (random examples per class)", per_row=args.n_per_class)

    errors = stats[~stats["correct"]].sort_values("confidence", ascending=False).index[: args.n_gallery]
    plot_gradcam_grid([item(i) for i in errors], out_dir / "gradcam_confident_errors.png",
                      "Most confident misclassifications")

    if "focus_ratio" in stats:
        low = stats.dropna(subset=["focus_ratio"]).sort_values("focus_ratio").index[: args.n_gallery]
        plot_gradcam_grid([item(i) for i in low], out_dir / "gradcam_least_lesion_focus.png",
                          "Lowest focus ratio: attention least on the lesion")

    # --- Summary ---
    md = [f"# Grad-CAM attention analysis: {args.run.name}", "",
          f"Split: {args.split} ({len(stats)} images). Heatmaps explain the "
          f"{'predicted class' if args.target == 'pred' else 'true diagnosis'}.", ""]
    if "focus_ratio" in stats:
        s = stats.dropna(subset=["focus_ratio"])
        md += ["**Focus ratio** = mean heat inside the lesion / mean heat outside it (1 = no more "
               "attention on the lesion than on surrounding skin). **Peak on lesion** = share of images "
               "whose hottest point is on the lesion. **Attention not on lesion** = share with focus "
               "ratio <= 1. The heatmap share on the lesion depends on lesion size, so read it next to "
               "the lesion area.", ""]
        overall = pd.DataFrame([describe(s)], index=["all images"])
        by_outcome = pd.DataFrame({k: describe(g) for k, g in s.groupby(
            s["correct"].map({True: "correct", False: "incorrect"}))}).T
        by_dx = pd.DataFrame({k: describe(g) for k, g in s.groupby("dx")}).T
        md += ["## Overall", "", md_table(pd.concat([overall, by_outcome]), "Group"), "",
               "## By true diagnosis", "", md_table(by_dx, "Diagnosis"), ""]
    (out_dir / "summary.md").write_text("\n".join(md))
    print("\n".join(md))
    print(f"Figures and statistics saved to {out_dir}/")


if __name__ == "__main__":
    main()
