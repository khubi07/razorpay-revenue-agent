import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib


# ============================================================
# 1. LOAD TRAINING DATA
# ============================================================

df = pd.read_csv("data/training_data.csv")


# ============================================================
# 2. SELECT FEATURES
# ============================================================

features = [
    "co_purchase_count",
    "candidate_price",
    "cart_price",
    "customer_aov",
    "total_orders",
    "candidate_price_ratio"
]

X = df[features]
y = df["accepted"]


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# 4. CREATE MODEL PIPELINE
# ============================================================

model = Pipeline(
    [
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000
            )
        )
    ]
)


# ============================================================
# 5. TRAIN
# ============================================================

model.fit(X_train, y_train)


print("Model trained successfully!")


# ============================================================
# 6. PREDICTIONS
# ============================================================

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# ============================================================
# 7. EVALUATION
# ============================================================

print("\n===== MODEL PERFORMANCE =====")

print(
    f"Accuracy  : "
    f"{accuracy_score(y_test, y_pred):.4f}"
)

print(
    f"Precision : "
    f"{precision_score(y_test, y_pred):.4f}"
)

print(
    f"Recall    : "
    f"{recall_score(y_test, y_pred):.4f}"
)

print(
    f"ROC-AUC   : "
    f"{roc_auc_score(y_test, y_probability):.4f}"
)

print("\n===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_test,
        y_pred
    )
)


# ============================================================
# 8. SAVE MODEL
# ============================================================

joblib.dump(
    model,
    "ml/acceptance_model.pkl"
)

print("\nModel saved to:")
print("ml/acceptance_model.pkl")