"""One-class SVM fitting and prediction.

The model is not stored on disk. Fitting is deterministic (gamma='auto',
nu=1/n_train, no random seed) and takes milliseconds, so each class's stored
training.out is the model. This avoids pickle/scikit-learn version drift.

The scaler and the SVM are wrapped in a Pipeline so candidate points can never
be scaled with anything other than the training-fitted scaler.
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

from .features import FEATURES, load_training


def fit(X):
    """Fit the scaler + one-class SVM pipeline on training points."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("svm", OneClassSVM(kernel="rbf", gamma="auto", nu=1 / len(X))),
    ]).fit(X)


def load_model(training_path):
    """Fit a class model from its stored training distribution.

    Returns (pipeline, training_dataframe, coverage_filter_applied).
    """
    df_train, filter_applied = load_training(training_path)
    return fit(df_train[FEATURES].values), df_train, filter_applied


def predict(model, df_candidates):
    """Predict each candidate from its alignments against one class database.

    A candidate is called functional if any of its alignments falls inside the
    SVM boundary. The reported homolog is the alignment with the highest
    target TM-score.
    """
    results = []

    for query, df_query in df_candidates.groupby("query", sort=True):
        if df_query.empty:
            continue

        scores = model.decision_function(df_query[FEATURES].values)
        best_row = df_query.loc[df_query["ttmscore"].idxmax()]

        results.append({
            "candidate": query,
            "prediction": "yes" if scores.max() >= 0 else "no",
            "decision_value": round(float(scores.max()), 4),
            "best_subject_tmscore": best_row["subject"],
            "TM-score": round(float(best_row["ttmscore"]), 4),
            "seqID": round(float(best_row["seqID"]), 2),
            "candidate_coverage": round(float(best_row["coverage"]), 3),
            "n_alignments": len(df_query),
        })

    return results
