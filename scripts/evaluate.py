"""Evaluate a trained model on the internal test split and the external ISIC 2018 test set.

Reports, with 95% bootstrap confidence intervals (resampling lesions, not images):
  * overall accuracy, balanced accuracy, macro F1 and macro ROC-AUC
  * per-class sensitivity, specificity, PPV, F1 and ROC-AUC
  * two referral-style binary decisions, with thresholds chosen on the validation set:
      - malignant/premalignant (mel + bcc + akiec) vs benign
      - melanoma vs everything else
  * subgroup performance by sex, age band, body site, diagnosis method and source

Example:
    python scripts/evaluate.py --run runs/efficientnet_b0_weighted_loss_20261109-2100
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score
from torch.utils.data import DataLoader

from melancare.data import CLASS_NAMES, MALIGNANT, SkinLesionDataset, build_transforms
from melancare.engine import predict
from melancare.metrics import (
    binary_metrics,
    bootstrap_ci,
    per_class_metrics,
    summary_metrics,
    threshold_for_sensitivity,
)
from melancare.model import get_device, load_checkpoint
from melancare.plots import plot_binary_roc, plot_confusion_matrix, plot_roc_curves

SET_TITLES = {
    "val": "Validation",
    "test": "Internal test (HAM10000, held-out lesions)",
    "external": "External test (ISIC 2018 Task 3 test set)",
}
BINARY_TASKS = {"malignant": "Malignant/premalignant vs benign", "melanoma": "Melanoma vs rest"}
METRIC_LABELS = {"accuracy": "Accuracy", "balanced_accuracy": "Balanced accuracy",
                 "macro_f1": "Macro F1", "macro_auc": "Macro AUC"}


def add_predictions(df: pd.DataFrame, probs: np.ndarray, classes: list[str]) -> pd.DataFrame:
    out = df.reset_index(drop=True).copy()
    out["y"] = out["dx"].map(classes.index)
    out["pred_dx"] = [classes[i] for i in probs.argmax(1)]
    for k, c in enumerate(classes):
        out[f"p_{c}"] = probs[:, k]
    out["malignant_true"] = out["dx"].isin(MALIGNANT)
    out["malignant_score"] = probs[:, [classes.index(c) for c in MALIGNANT]].sum(1)
    out["melanoma_true"] = out["dx"] == "mel"
    out["melanoma_score"] = probs[:, classes.index("mel")]
    return out


def subgroup_table(df: pd.DataFrame, thresholds: dict, min_n: int = 30) -> pd.DataFrame:
    df = df.copy()
    df["age_band"] = pd.cut(df["age"], [0, 30, 50, 70, np.inf], right=False,
                            labels=["<30", "30-49", "50-69", "70+"])
    rows = []
    for col in ["sex", "age_band", "localization", "dx_type", "dataset"]:
        if col not in df:
            continue
        for value, g in df.groupby(col, observed=True):
            if len(g) < min_n:
                continue
            mal = binary_metrics(g["malignant_true"].to_numpy(), g["malignant_score"].to_numpy(),
                                 thresholds["malignant"])
            rows.append({
                "attribute": col, "group": value, "n": len(g), "n_malignant": mal["n_positive"],
                "accuracy": (g["dx"] == g["pred_dx"]).mean(),
                "balanced_accuracy": balanced_accuracy_score(g["dx"], g["pred_dx"]),
                "malignant_sensitivity": mal["sensitivity"],
                "malignant_specificity": mal["specificity"],
                "malignant_auc": mal["auc"],
            })
    return pd.DataFrame(rows)


def fmt(value: float, ci: tuple[float, float] | None = None) -> str:
    if value is None or np.isnan(value):
        return "n/a"
    return f"{value:.3f}" if ci is None else f"{value:.3f} ({ci[0]:.3f}-{ci[1]:.3f})"


def md_table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(lines)


def evaluate_set(name: str, df: pd.DataFrame, classes: list[str], thresholds: dict,
                 out_dir: Path, n_boot: int) -> tuple[dict, str]:
    y = df["y"].to_numpy()
    probs = df[[f"p_{c}" for c in classes]].to_numpy()
    title = SET_TITLES[name]

    summary = summary_metrics(y, probs)
    per_class = per_class_metrics(y, probs, classes)
    binary = {task: binary_metrics(df[f"{task}_true"].to_numpy(), df[f"{task}_score"].to_numpy(), thr)
              for task, thr in thresholds.items()}

    def on_resample(idx: np.ndarray) -> dict[str, float]:
        res = {f"overall/{k}": v for k, v in summary_metrics(y[idx], probs[idx]).items()}
        pc = per_class_metrics(y[idx], probs[idx], classes)
        for c in classes:
            res[f"{c}/sensitivity"] = pc.loc[c, "sensitivity"]
            res[f"{c}/auc"] = pc.loc[c, "auc"]
        for task, thr in thresholds.items():
            b = binary_metrics(df[f"{task}_true"].to_numpy()[idx], df[f"{task}_score"].to_numpy()[idx], thr)
            for k in ("sensitivity", "specificity", "auc"):
                res[f"{task}/{k}"] = b[k]
        return res

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ci = bootstrap_ci(on_resample, len(y), groups=df["lesion_id"].to_numpy(), n_boot=n_boot)

    # Figures
    plot_confusion_matrix(y, probs.argmax(1), classes, out_dir / f"confusion_{name}.png", title)
    plot_roc_curves(y, probs, classes, out_dir / f"roc_{name}.png", f"{title}: one-vs-rest ROC")
    for task in thresholds:
        plot_binary_roc(df[f"{task}_true"], df[f"{task}_score"], binary[task],
                        out_dir / f"roc_{task}_{name}.png", f"{BINARY_TASKS[task]}\n{title}")

    # Tables
    pc_out = per_class.copy()
    for c in classes:
        for k in ("sensitivity", "auc"):
            pc_out.loc[c, f"{k}_ci_low"], pc_out.loc[c, f"{k}_ci_high"] = ci[f"{c}/{k}"]
    pc_out.to_csv(out_dir / f"per_class_{name}.csv")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        subgroups = subgroup_table(df, thresholds)
    subgroups.to_csv(out_dir / f"subgroups_{name}.csv", index=False)

    # Markdown report section
    md = [f"## {title}", "",
          f"{len(df)} images from {df['lesion_id'].nunique()} lesions. "
          f"95% confidence intervals from {n_boot:,} lesion-level bootstrap resamples.", ""]
    md.append(md_table(["Metric", "Value (95% CI)"], [
        [METRIC_LABELS[k], fmt(v, ci[f"overall/{k}"])] for k, v in summary.items()
    ]))
    md += ["", "### Per class", ""]
    md.append(md_table(
        ["Class", "n", "Sensitivity (95% CI)", "Specificity", "PPV", "F1", "AUC (95% CI)"],
        [[f"{c} ({CLASS_NAMES[c]})", int(r["support"]), fmt(r["sensitivity"], ci[f"{c}/sensitivity"]),
          fmt(r["specificity"]), fmt(r["ppv"]), fmt(r["f1"]), fmt(r["auc"], ci[f"{c}/auc"])]
         for c, r in per_class.iterrows()],
    ))
    md += ["", "### Referral decisions", "",
           "Thresholds were fixed on the validation set to reach the target sensitivity there, "
           "then applied unchanged here.", ""]
    md.append(md_table(
        ["Task", "Positives / negatives", "Sensitivity (95% CI)", "Specificity (95% CI)", "PPV", "NPV",
         "AUC (95% CI)"],
        [[BINARY_TASKS[t], f"{b['n_positive']} / {b['n_negative']}",
          fmt(b["sensitivity"], ci[f"{t}/sensitivity"]), fmt(b["specificity"], ci[f"{t}/specificity"]),
          fmt(b["ppv"]), fmt(b["npv"]), fmt(b["auc"], ci[f"{t}/auc"])] for t, b in binary.items()],
    ))
    if len(subgroups):
        md += ["", "### Subgroups (groups with at least 30 images)", ""]
        md.append(md_table(
            ["Attribute", "Group", "n", "Malignant n", "Balanced acc.", "Malignant sens.",
             "Malignant spec.", "Malignant AUC"],
            [[r.attribute, r.group, r.n, r.n_malignant, fmt(r.balanced_accuracy),
              fmt(r.malignant_sensitivity), fmt(r.malignant_specificity), fmt(r.malignant_auc)]
             for r in subgroups.itertuples()],
        ))
    md.append("")

    result = {"summary": summary, "per_class": per_class.to_dict(orient="index"), "binary": binary,
              "ci": {k: list(v) for k, v in ci.items()}}
    return result, "\n".join(md)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", type=Path, required=True, help="Run directory containing best.pt")
    p.add_argument("--data-dir", type=Path, default=Path("data/processed"))
    p.add_argument("--target-sensitivity", type=float, default=0.90)
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--num-workers", type=int, default=4)
    p.add_argument("--device", default=None)
    args = p.parse_args()

    device = get_device(args.device)
    model, ckpt = load_checkpoint(args.run, device)
    classes = ckpt["classes"]
    transform = build_transforms(ckpt["img_size"], train=False)
    out_dir = args.run / "evaluation"
    out_dir.mkdir(exist_ok=True)

    splits = pd.read_csv(args.data_dir / "splits.csv")
    sets = {name: splits[splits["split"] == name] for name in ("val", "test")}
    if (args.data_dir / "external_test.csv").exists():
        sets["external"] = pd.read_csv(args.data_dir / "external_test.csv")

    preds = {}
    for name, df in sets.items():
        print(f"Predicting {name} ({len(df)} images)...")
        loader = DataLoader(SkinLesionDataset(df, args.data_dir / "images", transform),
                            batch_size=args.batch_size, num_workers=args.num_workers)
        probs, _ = predict(model, loader, device)
        preds[name] = add_predictions(df, probs, classes)
        preds[name].to_csv(out_dir / f"predictions_{name}.csv", index=False)

    val = preds["val"]
    thresholds = {task: threshold_for_sensitivity(val[f"{task}_true"].to_numpy(),
                                                  val[f"{task}_score"].to_numpy(),
                                                  args.target_sensitivity)
                  for task in BINARY_TASKS}

    report = [f"# Evaluation: {args.run.name}", "",
              f"Model: {ckpt['arch']}, best epoch {ckpt['epoch']} "
              f"(validation balanced accuracy {ckpt['val_metrics']['balanced_accuracy']:.3f}).",
              f"Referral thresholds set on validation for {args.target_sensitivity:.0%} sensitivity: "
              + ", ".join(f"{t} >= {v:.3f}" for t, v in thresholds.items()) + ".", ""]
    results = {"thresholds": thresholds, "target_sensitivity": args.target_sensitivity}
    for name in [n for n in ("test", "external") if n in preds]:
        print(f"Evaluating {name} (bootstrap x{args.n_boot})...")
        results[name], section = evaluate_set(name, preds[name], classes, thresholds, out_dir, args.n_boot)
        report.append(section)

    (out_dir / "metrics.json").write_text(json.dumps(results, indent=2, default=float))
    (out_dir / "report.md").write_text("\n".join(report))
    print("\n".join(report))
    print(f"\nFigures, tables and report saved to {out_dir}/")


if __name__ == "__main__":
    main()
