import pandas as pd


# Load training data
df = pd.read_csv("data/training_data.csv")


print("===== TRAINING DATA SUMMARY =====")

print(f"Rows    : {len(df)}")
print(f"Columns : {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\n===== TARGET DISTRIBUTION =====")

print(df["accepted"].value_counts())

print("\nTarget percentages:")
print(
    (df["accepted"].value_counts(normalize=True) * 100)
    .round(2)
)


# ============================================================
# FEATURE SUMMARY
# ============================================================

print("\n===== FEATURE SUMMARY =====")

print(
    df[
        [
            "co_purchase_count",
            "candidate_price",
            "cart_price",
            "customer_aov",
            "total_orders",
            "candidate_price_ratio"
        ]
    ].describe()
)


# ============================================================
# EXAMPLE POSITIVE CASES
# ============================================================

print("\n===== POSITIVE EXAMPLES =====")

print(
    df[df["accepted"] == 1]
    .head(5)
    .to_string(index=False)
)


# ============================================================
# EXAMPLE NEGATIVE CASES
# ============================================================

print("\n===== NEGATIVE EXAMPLES =====")

print(
    df[df["accepted"] == 0]
    .head(5)
    .to_string(index=False)
)