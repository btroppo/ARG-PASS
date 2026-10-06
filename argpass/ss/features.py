"""Shared parsing of Foldseek easy-search output.

Both the training distribution and the candidate search are parsed here so the
derived columns (seqID, coverage) can never drift between the two.

The column order must match the --format-output string used in foldseek.py.
"""

import pandas as pd

COLUMNS = [
    "query", "subject", "tmscore", "qtmscore", "ttmscore",
    "id", "qlen", "alnlen", "tlen",
]

FEATURES = ["seqID", "ttmscore"]

# Coverage bounds applied to the training distribution (see should_filter_coverage).
COVERAGE_MIN = 0.90
COVERAGE_MAX = 1.10

# Minimum number of ARP structures in a class for the coverage filter to be applied.
MIN_STRUCTURES_FOR_COVERAGE_FILTER = 10


def load_foldseek(path, drop_self=False):
    """Read a Foldseek easy-search output file and add the derived columns.

    seqID is the alignment-length-weighted percent identity, i.e. pident scaled
    by the fraction of the target covered by the alignment. coverage is the
    target length relative to the query length.
    """
    df = pd.read_csv(path, sep="\t", header=None, names=COLUMNS)

    df["query"] = df["query"].str.replace(r"\.pdb$", "", regex=True)
    df["subject"] = df["subject"].str.replace(r"\.pdb$", "", regex=True)

    df["seqID"] = (df.alnlen / df.tlen) * df.id
    df["coverage"] = df.tlen / df.qlen

    if drop_self:
        df = df[df["query"] != df["subject"]]

    return df.reset_index(drop=True)


def count_structures(df):
    """Number of distinct ARP structures represented in a training distribution."""
    return len(set(df["query"]) | set(df["subject"]))


def should_filter_coverage(df):
    """Whether the coverage filter should be applied to this training set.

    The filter removes alignments whose target/query length ratio falls outside
    COVERAGE_MIN..COVERAGE_MAX, where the TM-score and seqID values are less
    trustworthy. It is only applied when the class has at least
    MIN_STRUCTURES_FOR_COVERAGE_FILTER structures, so that discarding those
    points does not leave too few training points behind.
    """
    return count_structures(df) >= MIN_STRUCTURES_FOR_COVERAGE_FILTER


def apply_coverage_filter(df):
    """Keep only alignments within the trusted coverage range."""
    return df[df["coverage"].between(COVERAGE_MIN, COVERAGE_MAX)].reset_index(drop=True)


def load_training(path):
    """Load a class training distribution, ready for fitting.

    Self-hits are dropped, and the coverage filter is applied only if the class
    has enough structures to afford it. Returns (dataframe, filter_applied).
    """
    df = load_foldseek(path, drop_self=True)

    filter_applied = should_filter_coverage(df)
    if filter_applied:
        df = apply_coverage_filter(df)

    if df.empty:
        raise ValueError(f"No training points left after filtering: {path}")

    return df, filter_applied


def load_candidates(path):
    """Load candidate alignments.

    The coverage filter is deliberately NOT applied to candidates: it describes
    the trustworthiness of the training distribution, not a criterion for
    rejecting a query. Coverage is still reported in the output so users can
    judge individual hits.
    """
    return load_foldseek(path, drop_self=True)
