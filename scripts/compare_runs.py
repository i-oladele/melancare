"""Compare evaluated runs side by side (e.g. different class-imbalance strategies).

Reads <run>/config.json and <run>/evaluation/metrics.json from each run and prints
markdown tables for the internal and external test sets.

Example:
    python scripts/compare_runs.py runs/effb0_none runs/effb0_sampler runs/effb0_weighted
    python scripts/compare_runs.py runs/* --out docs/imbalance_comparison.md
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melancare.data import CLASSES

SETS = {"test": "Internal test (HAM10000)", "external": "External test (ISIC 2018)"}


def fmt(v: float, ci: list[float] | None = None) -> str:
    return f"{v:.3f}" if ci is None else f"{v:.3f} ({ci[0]:.2f}-{ci[1]:.2f})"


def table(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    return "\n".join(out + ["| " + " | ".join(r) + " |" for r in rows])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("runs", nargs="+", type=Path)
    p.add_argument("--out", type=Path, default=None, help="Also write the tables to this markdown file.")
    args = p.parse_args()

    runs = []
    for run in args.runs:
        metrics_path = run / "evaluation" / "metrics.json"
        if not metrics_path.exists():
            print(f"Skipping {run}: no evaluation/metrics.json")
            continue
        config = json.loads((run / "config.json").read_text())
        runs.append((config.get("imbalance", run.name), json.loads(metrics_path.read_text())))

    md = []
    for key, title in SETS.items():
        present = [(name, m[key]) for name, m in runs if key in m]
        if not present:
            continue
        md += [f"### {title}", "", "Overall (95% CI) and referral performance at the validation-set threshold:", ""]
        md.append(table(
            ["Imbalance method", "Balanced accuracy", "Macro AUC", "Macro F1", "Accuracy",
             "Malignant sens. / spec.", "Melanoma sens. / spec."],
            [[name, fmt(m["summary"]["balanced_accuracy"], m["ci"]["overall/balanced_accuracy"]),
              fmt(m["summary"]["macro_auc"]), fmt(m["summary"]["macro_f1"]), fmt(m["summary"]["accuracy"]),
              f"{m['binary']['malignant']['sensitivity']:.3f} / {m['binary']['malignant']['specificity']:.3f}",
              f"{m['binary']['melanoma']['sensitivity']:.3f} / {m['binary']['melanoma']['specificity']:.3f}"]
             for name, m in present],
        ))
        md += ["", "Sensitivity per class (arg-max prediction):", ""]
        md.append(table(
            ["Imbalance method", *CLASSES],
            [[name, *[fmt(m["per_class"][c]["sensitivity"]) for c in CLASSES]] for name, m in present],
        ))
        md.append("")

    text = "\n".join(md)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
        print(f"\nWritten to {args.out}")


if __name__ == "__main__":
    main()
