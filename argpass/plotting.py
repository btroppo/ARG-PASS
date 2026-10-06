"""Figures for a class: the seqID vs TM-score distribution and the SVM boundary.

Ported from the notebook's plotting cell. Candidate colours are assigned from
the candidates actually present in the results rather than by listing a
directory, so figures are reproducible from the data alone.
"""

import matplotlib
matplotlib.use("Agg")  # no display on a server

import matplotlib.pyplot as plt
import numpy as np

from .features import FEATURES

TRAIN_COLOUR = "lightskyblue"
MAX_LEGEND_ENTRIES = 20


def _colour_map(queries):
    colours = [plt.cm.tab20(i % 20) for i in range(len(queries))]
    return {q: colours[i] for i, q in enumerate(queries)}


def distribution_plot(df_train, df_candidates, out_path, title=None):
    """Unscaled seqID vs TM-score, training distribution with candidates over it."""
    queries = sorted(df_candidates["query"].unique())
    colours = _colour_map(queries)
    show_legend = len(queries) <= MAX_LEGEND_ENTRIES

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(df_train["seqID"], df_train["ttmscore"],
               s=50, color=TRAIN_COLOUR, label="Subject proteins")

    for query in queries:
        df_query = df_candidates[df_candidates["query"] == query]
        ax.scatter(df_query["seqID"], df_query["ttmscore"],
                   s=100, color=colours[query], edgecolors="k",
                   label=query if show_legend else None)

    ax.set_title(title or "seqID vs TM-score: subjects and candidates", fontsize=16)
    ax.set_xlabel("seqID", fontsize=14)
    ax.set_ylabel("TM-score", fontsize=14)
    ax.grid(True)
    if show_legend:
        ax.legend(loc="best", fontsize=10)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path


def boundary_plot(model, df_train, df_candidates, out_path, title=None):
    """Scaled feature space with the one-class SVM decision boundary."""
    scaler = model.named_steps["scaler"]
    svm = model.named_steps["svm"]

    X_train_scaled = scaler.transform(df_train[FEATURES].values)

    queries = sorted(df_candidates["query"].unique())
    colours = _colour_map(queries)
    show_legend = len(queries) <= MAX_LEGEND_ENTRIES

    xx, yy = np.meshgrid(
        np.linspace(X_train_scaled[:, 0].min() - 1, X_train_scaled[:, 0].max() + 1, 500),
        np.linspace(X_train_scaled[:, 1].min() - 1, X_train_scaled[:, 1].max() + 1, 500),
    )
    Z = svm.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.contourf(xx, yy, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.PuBu)
    ax.contour(xx, yy, Z, levels=[0], linewidths=2, colors="red")
    ax.scatter(X_train_scaled[:, 0], X_train_scaled[:, 1],
               c=TRAIN_COLOUR, s=50, label="Training points")

    for query in queries:
        df_query = df_candidates[df_candidates["query"] == query]
        X_query_scaled = scaler.transform(df_query[FEATURES].values)
        ax.scatter(X_query_scaled[:, 0], X_query_scaled[:, 1],
                   s=100, color=colours[query], edgecolors="k",
                   label=query if show_legend else None)

    ax.set_title(title or "One-Class SVM decision boundary", fontsize=16)
    ax.set_xlabel("seqID (scaled)", fontsize=14)
    ax.set_ylabel("TM-score (scaled)", fontsize=14)
    ax.grid(True)
    if show_legend:
        ax.legend(loc="lower right", fontsize=10)

    fig.tight_layout()
    fig.savefig(out_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    return out_path
