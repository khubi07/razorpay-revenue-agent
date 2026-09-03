import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from agent import validate_agent_decision


# ------------------------------------------------------------
# Fake trusted recommendation produced by our Python engine
# ------------------------------------------------------------

recommendations = {
    "action": "cross_sell",
    "candidate": {
        "product_id": "P003",
        "product_name": "USB-C Cable",
        "action_type": "cross_sell",
        "price": 299,
        "cost_price": 211.72,
        "inventory": 24,
        "margin_percentage": 0.2919,
    }
}


# ------------------------------------------------------------
# Fake merchant rules
# ------------------------------------------------------------

merchant_rules = {
    "minimum_margin_percentage": 0.20,
    "max_discount": 0.10,
    "max_incentive": 500,
    "allowed_actions": [
        "cross_sell",
        "upsell"
    ]
}


# ------------------------------------------------------------
# Test helper
# ------------------------------------------------------------

def run_test(test_name, decision, expected_valid):

    result = validate_agent_decision(
        decision=decision,
        recommendations=recommendations,
        merchant_rules=merchant_rules
    )

    actual_valid = result.get("valid")

    print(f"\n===== {test_name} =====")
    print(json.dumps(result, indent=2, default=str))

    if actual_valid == expected_valid:
        print("PASS")
    else:
        print("FAIL")


# ------------------------------------------------------------
# Test 1: Valid decision
# ------------------------------------------------------------

run_test(
    test_name="Valid recommendation",
    decision={
        "action": "cross_sell",
        "product_id": "P003",
        "reason": "Recommend the validated USB-C Cable."
    },
    expected_valid=True
)


# ------------------------------------------------------------
# Test 2: Gemini selects a product not recommended by Python
# ------------------------------------------------------------

run_test(
    test_name="Wrong product ID",
    decision={
        "action": "cross_sell",
        "product_id": "P999",
        "reason": "Recommend another product."
    },
    expected_valid=False
)


# ------------------------------------------------------------
# Test 3: Gemini selects an action not allowed by merchant rules
# ------------------------------------------------------------

run_test(
    test_name="Disallowed action",
    decision={
        "action": "discount",
        "product_id": "P003",
        "reason": "Offer a discount."
    },
    expected_valid=False
)