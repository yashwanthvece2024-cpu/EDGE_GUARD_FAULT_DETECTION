import numpy as np
import joblib

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from config import MODEL_FILE


np.random.seed(42)


def create_dataset():

    normal = np.column_stack([
        np.random.normal(40, 5, 700),
        np.random.normal(0.8, 0.20, 700),
        np.random.normal(0.15, 0.06, 700)
    ])

    warning = np.column_stack([
        np.random.normal(62, 7, 500),
        np.random.normal(1.8, 0.35, 500),
        np.random.normal(0.48, 0.12, 500)
    ])

    fault = np.column_stack([
        np.random.normal(83, 7, 400),
        np.random.normal(3.0, 0.50, 400),
        np.random.normal(0.95, 0.20, 400)
    ])

    X = np.vstack([
        normal,
        warning,
        fault
    ])

    y = np.array(
        ["NORMAL"] * len(normal)
        + ["WARNING"] * len(warning)
        + ["FAULT"] * len(fault)
    )

    X[:, 0] = np.clip(X[:, 0], 20, 100)
    X[:, 1] = np.clip(X[:, 1], 0, 5)
    X[:, 2] = np.clip(X[:, 2], 0, 2)

    return X, y


def train():

    X, y = create_dataset()

    model = Pipeline([
        ("scaler", StandardScaler()),
        (
            "svm",
            SVC(
                kernel="rbf",
                probability=True,
                C=10,
                gamma="scale"
            )
        )
    ])

    model.fit(X, y)

    joblib.dump(model, MODEL_FILE)

    print()
    print("=" * 50)
    print("EDGEGUARD SVM MODEL CREATED")
    print("=" * 50)
    print(f"Model: {MODEL_FILE}")
    print(f"Samples: {len(X)}")
    print("Classes: NORMAL / WARNING / FAULT")
    print("=" * 50)


if __name__ == "__main__":
    train()