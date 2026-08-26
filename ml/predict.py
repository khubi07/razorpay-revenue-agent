import pandas as pd
import joblib


# ============================================================
# LOAD MODEL + DATA
# ============================================================

model = joblib.load(
    "ml/acceptance_model.pkl"
)

products = pd.read_csv(
    "data/products.csv"
)

customers = pd.read_csv(
    "data/customers.csv"
)

transactions = pd.read_csv(
    "data/transactions.csv"
)


# ============================================================
# HELPER LOOKUPS
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


# ============================================================
# CO-PURCHASE COUNT
# ============================================================

from itertools import combinations
from collections import Counter

pair_counts = Counter()

for transaction_id, group in transactions.groupby(
    "transaction_id"
):

    product_ids = group["product_id"].unique()

    for pair in combinations(
        sorted(product_ids),
        2
    ):
        pair_counts[pair] += 1


def get_co_purchase_count(
    product_a,
    product_b
):

    pair = tuple(
        sorted(
            [product_a, product_b]
        )
    )

    return pair_counts.get(
        pair,
        0
    )


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_acceptance(
    customer_id,
    cart_product,
    candidate_product
):

    candidate_price = product_price[
        candidate_product
    ]

    cart_price = product_price[
        cart_product
    ]

    aov = customer_aov[
        customer_id
    ]

    total_orders = customer_orders[
        customer_id
    ]

    co_purchase_count = get_co_purchase_count(
        cart_product,
        candidate_product
    )

    price_ratio = (
        candidate_price / cart_price
    )

    # Create feature row
    features = pd.DataFrame(
        [
            {
                "co_purchase_count":
                    co_purchase_count,

                "candidate_price":
                    candidate_price,

                "cart_price":
                    cart_price,

                "customer_aov":
                    aov,

                "total_orders":
                    total_orders,

                "candidate_price_ratio":
                    price_ratio
            }
        ]
    )

    probability = model.predict_proba(
        features
    )[0][1]

    return probability


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    customer_id = "C002"
    cart_product = "P001"
    candidate_product = "P003"

    probability = predict_acceptance(
        customer_id,
        cart_product,
        candidate_product
    )

    print(
        f"Customer: {customer_id}"
    )

    print(
        f"Cart product: {cart_product}"
    )

    print(
        f"Candidate: {candidate_product}"
    )

    print(
        f"Predicted acceptance probability: "
        f"{probability:.2%}"
    )