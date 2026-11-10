"""Prepare HAM10000 for training.

Reads images and lesion masks straight from the downloaded zip files (no extraction needed),
resizes them so the shorter side is 256 px, and writes lesion-level train/val/test splits.

Outputs in data/processed/:
    images/<image_id>.jpg        HAM10000 + ISIC 2018 test images
    masks/<image_id>.png         lesion segmentation masks (HAM10000 only)
    splits.csv                   HAM10000 metadata + train/val/test column
    external_test.csv            ISIC 2018 Task 3 test set (official held-out set)
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image
from tqdm import tqdm

from melancare.data import CLASSES, lesion_level_split


def resize_short_side(img: Image.Image, size: int, resample) -> Image.Image:
    w, h = img.size
    scale = size / min(w, h)
    return img.resize((round(w * scale), round(h * scale)), resample)


def convert_zip(zip_path: Path, out_dir: Path, size: int, masks: bool) -> int:
    """Resize every image in a zip into out_dir. Skips files already done. Returns count."""
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = ".png" if masks else ".jpg"
    done = 0
    with zipfile.ZipFile(zip_path) as zf:
        members = [
            m for m in zf.namelist()
            if m.lower().endswith(ext) and "__MACOSX" not in m and not Path(m).name.startswith("._")
        ]
        for member in tqdm(members, desc=zip_path.name):
            image_id = Path(member).stem.removesuffix("_segmentation")
            out = out_dir / f"{image_id}{ext}"
            done += 1
            if out.exists():
                continue
            with zf.open(member) as f, Image.open(f) as im:
                if masks:
                    resize_short_side(im.convert("L"), size, Image.NEAREST).save(out)
                else:
                    resize_short_side(im.convert("RGB"), size, Image.LANCZOS).save(out, quality=95)
    return done


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--size", type=int, default=256, help="Shorter side after resizing (px).")
    p.add_argument("--val-frac", type=float, default=0.15)
    p.add_argument("--test-frac", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    image_zips = sorted(
        z for z in args.raw_dir.glob("*.zip")
        if "segmentation" not in z.name.lower() and "GroundTruth" not in z.name
    )
    mask_zips = sorted(args.raw_dir.glob("*segmentation*.zip"))
    if not image_zips:
        sys.exit(f"No image zips found in {args.raw_dir}. See README for download instructions.")

    for z in image_zips:
        print(f"{z.name}: {convert_zip(z, args.out_dir / 'images', args.size, masks=False)} images")
    for z in mask_zips:
        print(f"{z.name}: {convert_zip(z, args.out_dir / 'masks', args.size, masks=True)} masks")

    # --- HAM10000: lesion-level splits ---
    meta = pd.read_csv(args.raw_dir / "HAM10000_metadata.csv")
    assert set(meta["dx"]) <= set(CLASSES), f"Unexpected labels: {set(meta['dx']) - set(CLASSES)}"
    available = {f.stem for f in (args.out_dir / "images").glob("*.jpg")}
    missing = set(meta["image_id"]) - available
    if missing:
        sys.exit(f"{len(missing)} HAM10000 images are missing (e.g. {sorted(missing)[:3]}). Is the download complete?")

    meta["split"] = lesion_level_split(meta, args.val_frac, args.test_frac, args.seed)
    leaks = meta.groupby("lesion_id")["split"].nunique().gt(1).sum()
    assert leaks == 0, f"{leaks} lesions appear in more than one split"
    meta.to_csv(args.out_dir / "splits.csv", index=False)

    # --- ISIC 2018 Task 3 official test set ---
    gt_path = args.raw_dir / "ISIC2018_Task3_Test_GroundTruth.csv"
    if gt_path.exists():
        ext = pd.read_csv(gt_path)
        ext = ext[ext["image_id"].isin(available)]
        overlap = set(ext["lesion_id"]) & set(meta["lesion_id"])
        print(f"\nExternal test set: {len(ext)} images; lesions shared with HAM10000: {len(overlap)}")
        ext.to_csv(args.out_dir / "external_test.csv", index=False)

    # --- Summary ---
    print("\nImages per class and split:")
    counts = pd.crosstab(meta["dx"], meta["split"])[["train", "val", "test"]]
    counts["total"] = counts.sum(1)
    print(counts.to_string())
    print("\nUnique lesions per split:")
    print(meta.groupby("split")["lesion_id"].nunique()[["train", "val", "test"]].to_string())


if __name__ == "__main__":
    main()
