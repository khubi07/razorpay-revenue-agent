from backend.agent.agent import validate_agent_decision


merchant_rules = {
    "minimum_margin_percentage": 0.2,
    "max_discount": 0.1,
    "max_incentive": 500,
    "allowed_actions": ["cross_sell", "upsell"],
}

valid_recommendations = {
    "action": "cross_sell",
    "candidate": {
        "product_id": "P003",
        "product_name": "USB-C Cable",
        "action_type": "cross_sell",
        "price": 299,
        "cost_price": 211.72,
        "inventory": 24,
    },
}


def run_test(name, decision, expected):
    result = validate_agent_decision(
        decision=decision,
        recommendations=valid_recommendations,
        merchant_rules=merchant_rules,
    )

    passed = result["valid"] == expected
    print(f"{'PASS' if passed else 'FAIL'} - {name}")
    print(result)

    assert passed


def test_valid_decision():
    run_test(
        "Valid decision",
        {
            "action": "cross_sell",
            "product_id": "P003",
            "reason": "Valid recommendation",
        },
        True,
    )


def test_invalid_action():
    run_test(
        "Disallowed action",
        {
            "action": "discount",
            "product_id": "P003",
            "reason": "Invalid action",
        },
        False,
    )


def test_wrong_product():
    run_test(
        "Wrong product",
        {
            "action": "cross_sell",
            "product_id": "P999",
            "reason": "Invalid product",
        },
        False,
    )


def test_wrong_action_type():
    run_test(
        "Action does not match recommendation",
        {
            "action": "upsell",
            "product_id": "P003",
            "reason": "Wrong action type",
        },
        False,
    )


def test_out_of_stock():
    recommendations = {
        **valid_recommendations,
        "candidate": {
            **valid_recommendations["candidate"],
            "inventory": 0,
        },
    }

    result = validate_agent_decision(
        decision={
            "action": "cross_sell",
            "product_id": "P003",
        },
        recommendations=recommendations,
        merchant_rules=merchant_rules,
    )

    assert result["valid"] is False
    print("PASS - Out-of-stock product")
    print(result)


def test_low_margin():
    recommendations = {
        **valid_recommendations,
        "candidate": {
            **valid_recommendations["candidate"],
            "cost_price": 250,
        },
    }

    result = validate_agent_decision(
        decision={
            "action": "cross_sell",
            "product_id": "P003",
        },
        recommendations=recommendations,
        merchant_rules=merchant_rules,
    )

    assert result["valid"] is False
    print("PASS - Low-margin product")
    print(result)