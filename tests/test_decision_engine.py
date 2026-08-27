import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.decision_engine import choose_best_candidate


# ============================================================
# COMMON MERCHANT RULES
# ============================================================

rules = {
    "minimum_expected_profit": 100,
    "minimum_margin": 100,
    "max_discount": 0.10,
    "max_incentive": 500,
    "allowed_actions": [
        "cross_sell",
        "upsell"
    ]
}


def run_test(name, candidates, expected_action):

    result = choose_best_candidate(
        candidates,
        rules
    )

    actual_action = result["action"]

    print(f"\n{name}")
    print(f"Expected : {expected_action}")
    print(f"Actual   : {actual_action}")

    if actual_action == expected_action:
        print("✅ PASS")
    else:
        print("❌ FAIL")


# ============================================================
# 1. NO CANDIDATES
# ============================================================

run_test(
    "1. No candidates",
    [],
    "do_nothing"
)


# ============================================================
# 2. OUT OF STOCK
# ============================================================

run_test(
    "2. Candidate out of stock",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.9,
            "profit": 500,
            "inventory": 0
        }
    ],
    "do_nothing"
)


# ============================================================
# 3. BELOW MINIMUM MARGIN
# ============================================================

run_test(
    "3. Below minimum margin",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.9,
            "profit": 50,
            "inventory": 20
        }
    ],
    "do_nothing"
)


# ============================================================
# 4. BELOW EXPECTED PROFIT THRESHOLD
# ============================================================

run_test(
    "4. Below expected-profit threshold",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.2,
            "profit": 200,
            "inventory": 20
        }
    ],
    "do_nothing"
)


# ============================================================
# 5. DISALLOWED ACTION
# ============================================================

run_test(
    "5. Disallowed action",
    [
        {
            "product_id": "P002",
            "action_type": "bundle",
            "acceptance_probability": 0.9,
            "profit": 500,
            "inventory": 20
        }
    ],
    "do_nothing"
)


# ============================================================
# 6. TWO VALID CANDIDATES
# ============================================================

run_test(
    "6. Choose highest expected profit",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.7,
            "profit": 300,
            "inventory": 20
        },
        {
            "product_id": "P003",
            "action_type": "cross_sell",
            "acceptance_probability": 0.8,
            "profit": 150,
            "inventory": 20
        }
    ],
    "cross_sell"
)


# ============================================================
# 7. ZERO ACCEPTANCE PROBABILITY
# ============================================================

run_test(
    "7. Zero acceptance probability",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.0,
            "profit": 500,
            "inventory": 20
        }
    ],
    "do_nothing"
)


# ============================================================
# 8. HIGH ACCEPTANCE PROBABILITY
# ============================================================

run_test(
    "8. High acceptance probability",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 1.0,
            "profit": 300,
            "inventory": 20
        }
    ],
    "cross_sell"
)


# ============================================================
# 9. NO CANDIDATE CLEARS THRESHOLD
# ============================================================

run_test(
    "9. Best candidate still below threshold",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.4,
            "profit": 200,
            "inventory": 20
        },
        {
            "product_id": "P003",
            "action_type": "cross_sell",
            "acceptance_probability": 0.3,
            "profit": 200,
            "inventory": 20
        }
    ],
    "do_nothing"
)


# ============================================================
# 10. MIXED VALID / INVALID CANDIDATES
# ============================================================

run_test(
    "10. Ignore invalid candidates and choose valid one",
    [
        {
            "product_id": "P002",
            "action_type": "cross_sell",
            "acceptance_probability": 0.9,
            "profit": 50,
            "inventory": 20
        },
        {
            "product_id": "P003",
            "action_type": "cross_sell",
            "acceptance_probability": 0.7,
            "profit": 300,
            "inventory": 20
        },
        {
            "product_id": "P004",
            "action_type": "cross_sell",
            "acceptance_probability": 0.9,
            "profit": 500,
            "inventory": 0
        }
    ],
    "cross_sell"
)