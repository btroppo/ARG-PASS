"""ARG-PASS command line interface.

Predicts antibiotic resistance function from protein structures by Foldseek
alignment against conserved ARP regions, followed by one-class SVM prediction.

Structure prediction and the DIAMOND pre-screen are not part of this package;
they run on the ARG-PASS webserver. This tool takes existing structures.
"""

import argparse
import os
import sys

import pandas as pd

from . import foldseek, plotting, svm
from .features import load_candidates

MODES = ["v2.0", "lddt"]
DB_NAME = "conserved_ARPs.pdb"
TRAINING_NAME = "training.out"


def class_dir(databases, mode, arg_class):
    return os.path.join(databases, mode, arg_class)


def available_classes(databases, mode):
    """Classes with both a database and a training distribution present."""
    root = os.path.join(databases, mode)
    if not os.path.isdir(root):
        raise FileNotFoundError(f"No databases for mode '{mode}' under {databases}")

    classes = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if os.path.isdir(d) and os.path.exists(os.path.join(d, TRAINING_NAME)):
            classes.append(name)

    if not classes:
        raise FileNotFoundError(f"No usable class databases under {root}")
    return classes


def run_class(arg_class, args, out_dir):
    """Search, predict and plot one ARG class. Returns a list of result rows."""
    d = class_dir(args.databases, args.mode, arg_class)
    training_path = os.path.join(d, TRAINING_NAME)
    database = os.path.join(d, DB_NAME)

    model, df_train, filter_applied = svm.load_model(training_path)

    aln_path = os.path.join(out_dir, f"{arg_class}_alignments.out")
    foldseek.search(args.input, database, aln_path,
                    binary=args.foldseek_bin,
                    exhaustive=not args.no_exhaustive,
                    threads=args.threads)

    df_candidates = load_candidates(aln_path)
    if df_candidates.empty:
        print(f"  {arg_class}: no alignments", file=sys.stderr)
        return []

    rows = svm.predict(model, df_candidates)
    for row in rows:
        row["ARG_class"] = arg_class
        row["mode"] = args.mode
        row["n_training_points"] = len(df_train)
        row["coverage_filter_applied"] = filter_applied

    if not args.no_plots:
        plotting.distribution_plot(
            df_train, df_candidates,
            os.path.join(out_dir, f"{arg_class}_seqID_vs_TM-score.png"),
            title=f"{arg_class} ({args.mode}): seqID vs TM-score")
        plotting.boundary_plot(
            model, df_train, df_candidates,
            os.path.join(out_dir, f"{arg_class}_SVM_boundary.png"),
            title=f"{arg_class} ({args.mode}): one-class SVM boundary")

    n_yes = sum(r["prediction"] == "yes" for r in rows)
    print(f"  {arg_class}: {n_yes}/{len(rows)} predicted functional")
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="arg-pass",
        description="Predict ARG function from protein structures.")
    p.add_argument("--input", required=True,
                   help="Directory of candidate .pdb structures")
    p.add_argument("--out", required=True,
                   help="Output CSV of predictions")
    p.add_argument("--mode", default="v2.0", choices=MODES,
                   help="Conserved-residue definition (default: v2.0)")
    p.add_argument("--class", dest="arg_class", default="all",
                   help="ARG class to test, or 'all' (default: all)")
    p.add_argument("--databases", default="databases",
                   help="Root of the databases directory (default: databases)")
    p.add_argument("--foldseek-bin", default=None,
                   help="Path to the foldseek executable")
    p.add_argument("--threads", type=int, default=None)
    p.add_argument("--no-plots", action="store_true",
                   help="Skip figure generation")
    p.add_argument("--no-exhaustive", action="store_true",
                   help="Disable --exhaustive-search (faster, may differ)")
    args = p.parse_args(argv)

    if not os.path.isdir(args.input):
        p.error(f"--input is not a directory: {args.input}")

    classes = (available_classes(args.databases, args.mode)
               if args.arg_class == "all" else [args.arg_class])

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)

    print(f"ARG-PASS mode={args.mode}, {len(classes)} class(es)")

    rows = []
    for arg_class in classes:
        try:
            rows.extend(run_class(arg_class, args, out_dir))
        except FileNotFoundError as exc:
            print(f"  {arg_class}: skipped ({exc})", file=sys.stderr)

    if not rows:
        print("No predictions produced.", file=sys.stderr)
        return 1

    columns = ["candidate", "ARG_class", "mode", "prediction","decision_value",
               "best_subject_tmscore", "TM-score", "seqID", "candidate_coverage",
               "n_training_points", "coverage_filter_applied"]
    df = pd.DataFrame(rows)[columns]
    df = df.sort_values(["candidate", "TM-score"], ascending=[True, False])
    df.to_csv(args.out, index=False)

    print(f"\nWrote {len(df)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
