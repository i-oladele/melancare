"""Fast tests that need no dataset or GPU."""

import numpy as np
import pandas as pd
import pytest
import torch
from torch import nn

from melancare.data import CLASSES, lesion_level_split
from melancare.gradcam import GradCAM, lesion_focus
from melancare.metrics import (
    binary_metrics,
    bootstrap_ci,
    per_class_metrics,
    summary_metrics,
    threshold_for_sensitivity,
)


@pytest.fixture
def fake_meta() -> pd.DataFrame:
    """700 lesions, 100 per class, each photographed 1-3 times."""
    rng = np.random.default_rng(0)
    rows = []
    for lesion in range(700):
        dx = CLASSES[lesion % len(CLASSES)]
        for k in range(rng.integers(1, 4)):
            rows.append({"lesion_id": f"L{lesion}", "image_id": f"I{lesion}_{k}", "dx": dx})
    return pd.DataFrame(rows)


def test_split_keeps_lesions_together(fake_meta):
    fake_meta["split"] = lesion_level_split(fake_meta)
    assert fake_meta["split"].notna().all()
    assert (fake_meta.groupby("lesion_id")["split"].nunique() == 1).all()
    lesion_split = fake_meta.groupby("lesion_id")["split"].first()
    assert lesion_split.value_counts(normalize=True)["test"] == pytest.approx(0.15, abs=0.01)
    # Every class appears in every split
    assert (pd.crosstab(fake_meta["dx"], fake_meta["split"]) > 0).all().all()


def test_split_rejects_inconsistent_labels(fake_meta):
    first = fake_meta.iloc[0]
    other_dx = "nv" if first["dx"] == "mel" else "mel"
    bad = pd.concat([fake_meta, pd.DataFrame([{**first, "image_id": "extra", "dx": other_dx}])])
    with pytest.raises(ValueError):
        lesion_level_split(bad)


def test_metrics_on_perfect_predictions():
    y = np.repeat(np.arange(3), 10)
    probs = np.eye(3)[y] * 0.9 + 0.1 / 3
    pc = per_class_metrics(y, probs, ["a", "b", "c"])
    assert (pc[["sensitivity", "specificity", "f1", "auc"]] == 1).all().all()
    assert summary_metrics(y, probs)["balanced_accuracy"] == 1


def test_metrics_known_confusion():
    # 4 of class 0 (3 correct), 4 of class 1 (all correct)
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    pred = np.array([0, 0, 0, 1, 1, 1, 1, 1])
    probs = np.eye(2)[pred]
    pc = per_class_metrics(y, probs, ["a", "b"])
    assert pc.loc["a", "sensitivity"] == 0.75
    assert pc.loc["b", "specificity"] == 0.75
    assert pc.loc["b", "ppv"] == pytest.approx(4 / 5)


def test_threshold_reaches_target_sensitivity():
    rng = np.random.default_rng(1)
    y = rng.random(500) < 0.2
    score = rng.random(500) + y * 0.3
    for target in (0.8, 0.9, 0.95):
        thr = threshold_for_sensitivity(y, score, target)
        assert binary_metrics(y, score, thr)["sensitivity"] >= target


def test_bootstrap_ci_contains_estimate():
    rng = np.random.default_rng(2)
    y = rng.integers(0, 2, 300)
    groups = np.repeat(np.arange(150), 2)
    ci = bootstrap_ci(lambda idx: {"mean": y[idx].mean()}, len(y), groups=groups, n_boot=200)
    lo, hi = ci["mean"]
    assert lo <= y.mean() <= hi


def test_gradcam_shape_and_range():
    torch.manual_seed(0)
    model = nn.Sequential(nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(), nn.Conv2d(8, 8, 3, padding=1),
                          nn.ReLU(), nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(8, 4))
    cam, logits = GradCAM(model, model[2])(torch.randn(2, 3, 32, 32))
    assert cam.shape == (2, 32, 32) and logits.shape == (2, 4)
    assert cam.min() >= 0 and cam.max() <= 1


def test_lesion_focus():
    mask = np.zeros((10, 10), bool)
    mask[:5] = True
    inside = mask.astype(float)
    f = lesion_focus(inside, mask)
    assert f["energy_in_lesion"] == 1 and f["lesion_area"] == 0.5 and f["focus_ratio"] > 100
    assert f["peak_in_lesion"]
    even = lesion_focus(np.ones((10, 10)), mask)
    assert even["focus_ratio"] == pytest.approx(1)
    off = lesion_focus(1 - inside, mask)
    assert off["focus_ratio"] < 0.01 and not off["peak_in_lesion"]
