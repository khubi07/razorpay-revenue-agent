import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


import pandas as pd

from ml.candidate_generator import CandidateGenerator
from ml.predict import predict_acceptance
from backend.decision_engine import choose_best_candidate


# ============================================================
# LOAD DATA
# ============================================================

products = pd.read_csv(
    "data/products.csv"
)

product_lookup = products.set_index(
    "product_id"
).to_dict("index")


# ============================================================
# CANDIDATE GENERATOR
# ============================================================

generator = CandidateGenerator(
    "data/transactions.csv",
    "data/products.csv"
)


# ============================================================
# MERCHANT RULES
# ============================================================

merchant_rules = {
    "minimum_margin_percentage": 0.20,

    "max_discount": 0.10,
    "max_incentive": 500,

    "allowed_actions": [
        "cross_sell",
        "upsell"
    ]
}


# ============================================================
# REVENUE PIPELINE
# ============================================================

def run_revenue_pipeline(
    customer_id,
    cart_product_ids
):

    # --------------------------------------------------------
    # For MVP, use first cart product as anchor
    # --------------------------------------------------------

    cart_product = cart_product_ids[0]

    # --------------------------------------------------------
    # 1. Generate candidates
    # --------------------------------------------------------

    candidates = generator.get_candidates(
        product_id=cart_product,
        customer_id=customer_id,
        cart_product_ids=cart_product_ids,
        top_k=5
    )

    # --------------------------------------------------------
    # No candidates
    # --------------------------------------------------------

    if not candidates:

        return {
            "action": "do_nothing",
            "candidate": None,
            "reason": "No valid candidates found."
        }

    # --------------------------------------------------------
    # 2. Add ML prediction + profit
    # --------------------------------------------------------

    enriched_candidates = []

    for candidate in candidates:

        product_id = candidate["product_id"]

        product_data = product_lookup[
            product_id
        ]

        # ML prediction
        acceptance_probability = predict_acceptance(
            customer_id=customer_id,
            cart_product=cart_product,
            candidate_product=product_id
        )

        # For MVP:
        # Assume product dataset contains cost_price.
        # If it doesn't, temporarily calculate profit
        # using a simple margin assumption.
        price = product_data["price"]
        cost_price = product_data["cost_price"]

        profit = price - cost_price

        # Determine action type
        cart_price = product_lookup[
            cart_product
        ]["price"]

        if price > cart_price:
            action_type = "upsell"
        else:
            action_type = "cross_sell"

        enriched_candidates.append({

    "product_id":
        product_id,

    "product_name":
        candidate["product_name"],

    "action_type":
        action_type,

    "acceptance_probability":
        acceptance_probability,

    "price":
        price,

    "cost_price":
        cost_price,

    "inventory":
        candidate["inventory"]
})

    # --------------------------------------------------------
    # 3. Decision engine
    # --------------------------------------------------------

    
    print("\n===== ENRICHED CANDIDATES =====")

    for candidate in enriched_candidates:
        print(candidate)

    print()

    decision = choose_best_candidate(
            enriched_candidates,
            merchant_rules
        )
    
    return decision
    
# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    customer_id = "C002"

    cart = [
        "P001"
    ]

    result = run_revenue_pipeline(
        customer_id,
        cart
    )

    print(
        "===== REVENUE PIPELINE ====="
    )

    print(result)