import pandas as pd
import numpy as np
from itertools import combinations
from collections import Counter


# ============================================================
# 1. LOAD DATA
# ============================================================

transactions = pd.read_csv("data/transactions.csv")
products = pd.read_csv("data/products.csv")
customers = pd.read_csv("data/customers.csv")


# ============================================================
# 2. BUILD CO-PURCHASE COUNTS
# ============================================================

pair_counts = Counter()

for transaction_id, group in transactions.groupby("transaction_id"):

    product_ids = group["product_id"].unique()

    for pair in combinations(sorted(product_ids), 2):
        pair_counts[pair] += 1


def get_co_purchase_count(product_a, product_b):

    pair = tuple(sorted([product_a, product_b]))

    return pair_counts.get(pair, 0)


# ============================================================
# 3. PRODUCT LOOKUPS
# ============================================================

product_price = dict(
    zip(
        products["product_id"],
        products["price"]
    )
)

customer_aov = dict(
    zip(
        customers["customer_id"],
        customers["average_order_value"]
    )
)

customer_orders = dict(
    zip(
        customers["customer_id"],
        customers["total_orders"]
    )
)

all_products = products["product_id"].tolist()


# ============================================================
# 4. CREATE TRAINING EXAMPLES
# ============================================================

examples = []


for transaction_id, group in transactions.groupby(
    "transaction_id"
):

    customer_id = group["customer_id"].iloc[0]

    purchased_products = set(
        group["product_id"]
    )

    # --------------------------------------------------------
    # Transactions with only one product cannot give us a
    # positive cross-sell example.
    # --------------------------------------------------------

    if len(purchased_products) < 2:
        continue

    # --------------------------------------------------------
    # Every product in this transaction can act as the
    # "cart product".
    # --------------------------------------------------------

    for cart_product in purchased_products:

        cart_price = product_price[cart_product]

        # Products actually purchased alongside cart product
        positive_candidates = (
            purchased_products - {cart_product}
        )

        for candidate_product in positive_candidates:

            candidate_price = product_price[
                candidate_product
            ]

            examples.append(
                [
                    customer_id,
                    cart_product,
                    candidate_product,

                    get_co_purchase_count(
                        cart_product,
                        candidate_product
                    ),

                    candidate_price,
                    cart_price,

                    customer_aov[customer_id],
                    customer_orders[customer_id],

                    1
                ]
            )

        # ----------------------------------------------------
        # NEGATIVE SAMPLING
        # ----------------------------------------------------

        # Products NOT purchased in this transaction
        negative_candidates = [
            product
            for product in all_products
            if product not in purchased_products
        ]

        # Sample up to 3 negatives
        sample_size = min(
            3,
            len(negative_candidates)
        )

        if sample_size == 0:
            continue

        sampled_negatives = np.random.choice(
            negative_candidates,
            size=sample_size,
            replace=False
        )

        for candidate_product in sampled_negatives:

            candidate_price = product_price[
                candidate_product
            ]

            examples.append(
                [
                    customer_id,
                    cart_product,
                    candidate_product,

                    get_co_purchase_count(
                        cart_product,
                        candidate_product
                    ),

                    candidate_price,
                    cart_price,

                    customer_aov[customer_id],
                    customer_orders[customer_id],

                    0
                ]
            )


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

columns = [
    "customer_id",
    "cart_product",
    "candidate_product",
    "co_purchase_count",
    "candidate_price",
    "cart_price",
    "customer_aov",
    "total_orders",
    "accepted"
]

training_data = pd.DataFrame(
    examples,
    columns=columns
)


# ============================================================
# 6. ADD PRICE RATIO
# ============================================================

training_data["candidate_price_ratio"] = (
    training_data["candidate_price"]
    / training_data["cart_price"]
)


# ============================================================
# 7. SAVE
# ============================================================

training_data.to_csv(
    "data/training_data.csv",
    index=False
)


# ============================================================
# 8. SUMMARY
# ============================================================

print("Corrected training dataset created successfully!")
print()

print(f"Total examples : {len(training_data)}")

print(
    f"Positive       : "
    f"{(training_data['accepted'] == 1).sum()}"
)

print(
    f"Negative       : "
    f"{(training_data['accepted'] == 0).sum()}"
)

print()

print("Positive %:")
print(
    round(
        (training_data["accepted"] == 1).mean() * 100,
        2
    )
)

print()
print("Saved to:")
print("data/training_data.csv")