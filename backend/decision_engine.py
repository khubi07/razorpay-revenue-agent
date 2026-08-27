def calculate_expected_revenue(
    acceptance_probability,
    price
):
    return acceptance_probability * price


def choose_best_candidate(
    candidates,
    merchant_rules
):
    """
    Select the revenue-growth action
    while respecting merchant rules.
    """

    valid_candidates = []

    minimum_margin_percentage = merchant_rules.get(
        "minimum_margin_percentage",
        0.20
    )

    allowed_actions = merchant_rules.get(
        "allowed_actions",
        ["cross_sell", "upsell"]
    )

    # --------------------------------------------------------
    # Check every candidate
    # --------------------------------------------------------

    for candidate in candidates:

        price = candidate["price"]
        cost_price = candidate["cost_price"]

        # 1. Inventory
        if candidate["inventory"] <= 0:
            continue

        # 2. Action type
        if candidate["action_type"] not in allowed_actions:
            continue

        # 3. Calculate margin percentage
        if price <= 0:
            continue

        profit = price - cost_price

        margin_percentage = profit / price

        if margin_percentage < minimum_margin_percentage:
            continue

        # 4. Validate acceptance probability
        probability = candidate[
            "acceptance_probability"
        ]

        if probability < 0 or probability > 1:
            continue

        # 5. Expected revenue
        expected_revenue = calculate_expected_revenue(
            probability,
            price
        )

        # Candidate passed all rules
        candidate = candidate.copy()

        candidate["profit"] = round(
            profit,
            2
        )

        candidate["margin_percentage"] = round(
            margin_percentage,
            4
        )

        candidate["expected_revenue"] = round(
            expected_revenue,
            2
        )

        valid_candidates.append(candidate)

    # --------------------------------------------------------
    # No valid candidate
    # --------------------------------------------------------

    if not valid_candidates:

        return {
            "action": "do_nothing",
            "candidate": None,
            "reason": (
                "No candidate satisfied the "
                "merchant's revenue and safety rules."
            )
        }

    # --------------------------------------------------------
    # Select highest expected revenue
    # --------------------------------------------------------

    best_candidate = max(
        valid_candidates,
        key=lambda x: x["expected_revenue"]
    )

    return {
        "action": best_candidate["action_type"],
        "candidate": best_candidate,
        "reason": (
            "Selected the candidate with the "
            "highest expected incremental revenue."
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    candidates = [

        {
            "product_id": "P002",
            "product_name": "Headphone Case",
            "action_type": "cross_sell",
            "acceptance_probability": 0.70,
            "price": 499,
            "cost_price": 250,
            "inventory": 24
        },

        {
            "product_id": "P003",
            "product_name": "USB-C Cable",
            "action_type": "cross_sell",
            "acceptance_probability": 0.60,
            "price": 299,
            "cost_price": 150,
            "inventory": 24
        }
    ]

    merchant_rules = {

        "minimum_margin_percentage": 0.20,

        "max_discount": 0.10,
        "max_incentive": 500,

        "allowed_actions": [
            "cross_sell",
            "upsell"
        ]
    }

    decision = choose_best_candidate(
        candidates,
        merchant_rules
    )

    print("===== AGENT DECISION =====")

    print(decision)