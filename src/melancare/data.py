"""Class definitions, lesion-level splitting, the PyTorch dataset and image transforms."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset
from torchvision import transforms as T

# Order matters: index i in a model's output is CLASSES[i].
CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]

CLASS_NAMES = {
    "akiec": "Actinic keratosis / intraepithelial carcinoma",
    "bcc": "Basal cell carcinoma",
    "bkl": "Benign keratosis-like lesion",
    "df": "Dermatofibroma",
    "mel": "Melanoma",
    "nv": "Melanocytic naevus",
    "vasc": "Vascular lesion",
}

# Malignant or premalignant classes, i.e. lesions that would usually be referred or biopsied.
MALIGNANT = ["akiec", "bcc", "mel"]

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def lesion_level_split(
    meta: pd.DataFrame, val_frac: float = 0.15, test_frac: float = 0.15, seed: int = 42
) -> pd.Series:
    """Return a train/val/test label for every image, keeping all images of a lesion together.

    HAM10000 contains several images of some lesions. Splitting by image would put
    near-identical photos in both training and test sets and inflate the scores.
    Splits are stratified by diagnosis so rare classes appear in every split.
    """
    if (meta.groupby("lesion_id")["dx"].nunique() > 1).any():
        raise ValueError("Some lesions have more than one diagnosis; cannot stratify by lesion.")

    lesion_dx = meta.groupby("lesion_id")["dx"].first()
    trainval, test = train_test_split(
        lesion_dx.index.to_numpy(),
        test_size=test_frac,
        stratify=lesion_dx.to_numpy(),
        random_state=seed,
    )
    train, val = train_test_split(
        trainval,
        test_size=val_frac / (1 - test_frac),
        stratify=lesion_dx.loc[trainval].to_numpy(),
        random_state=seed,
    )
    split_of = {lesion: "train" for lesion in train}
    split_of.update({lesion: "val" for lesion in val})
    split_of.update({lesion: "test" for lesion in test})
    return meta["lesion_id"].map(split_of)


class SkinLesionDataset(Dataset):
    """Loads `<image_dir>/<image_id>.jpg` and returns (image_tensor, class_index)."""

    def __init__(self, df: pd.DataFrame, image_dir: Path, transform):
        self.image_ids = df["image_id"].tolist()
        self.labels = df["dx"].map(CLASSES.index).tolist()
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_ids)

    def load_image(self, i: int) -> Image.Image:
        with Image.open(self.image_dir / f"{self.image_ids[i]}.jpg") as im:
            return im.convert("RGB")

    def __getitem__(self, i: int):
        return self.transform(self.load_image(i)), self.labels[i]


class RandomRot90:
    """Rotate by a random multiple of 90 degrees.

    Dermoscopic images have no natural "up", so rotations are label-preserving.
    Applied after a square crop, 90-degree rotations add no black corners.
    """

    def __call__(self, img: Image.Image) -> Image.Image:
        k = random.randint(0, 3)
        ops = [None, Image.Transpose.ROTATE_90, Image.Transpose.ROTATE_180, Image.Transpose.ROTATE_270]
        return img if k == 0 else img.transpose(ops[k])


def eval_geometry(img_size: int = 224, interpolation=T.InterpolationMode.BILINEAR) -> T.Compose:
    """Deterministic resize + centre crop used at evaluation time (also applied to masks)."""
    return T.Compose([T.Resize(img_size, interpolation=interpolation), T.CenterCrop(img_size)])


def build_transforms(img_size: int = 224, train: bool = False) -> T.Compose:
    normalise = [T.ToTensor(), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    if not train:
        return T.Compose([eval_geometry(img_size), *normalise])
    return T.Compose(
        [
            T.RandomResizedCrop(img_size, scale=(0.6, 1.0), ratio=(3 / 4, 4 / 3)),
            T.RandomHorizontalFlip(),
            T.RandomVerticalFlip(),
            RandomRot90(),
            # Colour carries diagnostic information, so keep colour changes mild.
            T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1, hue=0.02),
            *normalise,
        ]
    )


def denormalise(x) -> np.ndarray:
    """Convert a normalised CHW tensor back to an HWC float image in [0, 1] for plotting."""
    img = x.detach().cpu().numpy().transpose(1, 2, 0)
    img = img * np.array(IMAGENET_STD) + np.array(IMAGENET_MEAN)
    return np.clip(img, 0, 1)
