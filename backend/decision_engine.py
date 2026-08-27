def calculate_expected_profit(
    acceptance_probability,
    profit
):
    return acceptance_probability * profit


def choose_best_candidate(
    candidates,
    merchant_rules
):
    """
    Select the best revenue-growth action
    while respecting merchant rules.
    """

    valid_candidates = []

    minimum_expected_profit = merchant_rules.get(
        "minimum_expected_profit",
        100
    )

    minimum_margin = merchant_rules.get(
        "minimum_margin",
        100
    )

    allowed_actions = merchant_rules.get(
        "allowed_actions",
        ["cross_sell", "upsell"]
    )

    # --------------------------------------------------------
    # Check every candidate
    # --------------------------------------------------------

    for candidate in candidates:

        # 1. Inventory
        if candidate["inventory"] <= 0:
            continue

        # 2. Action type
        if candidate["action_type"] not in allowed_actions:
            continue

        # 3. Margin
        if candidate["profit"] < minimum_margin:
            continue

        # 4. Expected profit
        expected_profit = calculate_expected_profit(
            candidate["acceptance_probability"],
            candidate["profit"]
        )

        if expected_profit < minimum_expected_profit:
            continue

        # Candidate passed all rules
        candidate = candidate.copy()

        candidate["expected_profit"] = expected_profit

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
    # Select highest expected profit
    # --------------------------------------------------------

    best_candidate = max(
        valid_candidates,
        key=lambda x: x["expected_profit"]
    )

    return {
        "action": best_candidate["action_type"],
        "candidate": best_candidate,
        "reason": (
            "Selected the candidate with the "
            "highest expected incremental profit."
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
            "profit": 300,
            "inventory": 24
        },

        {
            "product_id": "P003",
            "product_name": "USB-C Cable",
            "action_type": "cross_sell",
            "acceptance_probability": 0.60,
            "profit": 120,
            "inventory": 24
        }
    ]

    merchant_rules = {

        "minimum_expected_profit": 100,
        "minimum_margin": 100,

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