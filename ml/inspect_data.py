import pandas as pd
from itertools import combinations
from collections import Counter


# Load data
products = pd.read_csv("data/products.csv")
customers = pd.read_csv("data/customers.csv")
transactions = pd.read_csv("data/transactions.csv")


# ============================================================
# 1. BASIC DATASET CHECK
# ============================================================

print("===== DATASET SUMMARY =====")

print(f"Products     : {len(products)}")
print(f"Customers    : {len(customers)}")
print(f"Transactions : {len(transactions)}")

print("\nMissing values:")
print(transactions.isnull().sum())


# ============================================================
# 2. MOST PURCHASED PRODUCTS
# ============================================================

print("\n===== TOP PRODUCTS =====")

product_counts = (
    transactions["product_id"]
    .value_counts()
    .head(10)
)

print(product_counts)


# ============================================================
# 3. PRODUCT CO-PURCHASES
# ============================================================

print("\n===== TOP CO-PURCHASED PRODUCT PAIRS =====")

pair_counts = Counter()

# Group products bought in the same transaction
for transaction_id, group in transactions.groupby("transaction_id"):

    products_in_transaction = group["product_id"].unique()

    for pair in combinations(
        sorted(products_in_transaction), 2
    ):
        pair_counts[pair] += 1


top_pairs = pair_counts.most_common(15)


# Convert product IDs to names
product_names = dict(
    zip(products["product_id"], products["name"])
)


for (product_a, product_b), count in top_pairs:

    name_a = product_names[product_a]
    name_b = product_names[product_b]

    print(
        f"{name_a} + {name_b} -> {count} purchases"
    )