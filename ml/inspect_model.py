import pandas as pd
import joblib


# Load model
model = joblib.load(
    "ml/acceptance_model.pkl"
)


# Feature names
features = [
    "co_purchase_count",
    "candidate_price",
    "cart_price",
    "customer_aov",
    "total_orders",
    "candidate_price_ratio"
]


# Get Logistic Regression coefficients
classifier = model.named_steps["classifier"]

coefficients = classifier.coef_[0]


# Create readable table
results = pd.DataFrame(
    {
        "feature": features,
        "coefficient": coefficients
    }
)


# Sort by absolute importance
results["absolute_coefficient"] = (
    results["coefficient"].abs()
)

results = results.sort_values(
    "absolute_coefficient",
    ascending=False
)


print("===== MODEL FEATURE COEFFICIENTS =====")

print(
    results[
        ["feature", "coefficient"]
    ].to_string(index=False)
)