from typing import Any


def validate_decision(
    decision: dict[str, Any],
    recommendations: list[dict[str, Any]],
    merchant_rules: dict[str, Any],
) -> dict[str, Any]:
    """
    Deterministic validation layer.
    The agent's decision cannot bypass these checks.
    """

    action = decision.get("action")
    product_id = decision.get("product_id")

    if not action or not product_id:
        return {
            "valid": False,
            "reason": "Decision must contain action and product_id.",
        }

    allowed_actions = merchant_rules.get("allowed_actions", [])

    if action not in allowed_actions:
        return {
            "valid": False,
            "reason": f"Action '{action}' is not allowed.",
        }

    candidate = next(
        (
            recommendation
            for recommendation in recommendations
            if recommendation.get("product_id") == product_id
        ),
        None,
    )

    if candidate is None:
        return {
            "valid": False,
            "reason": "Selected product is not a valid recommendation.",
        }

    inventory = candidate.get("inventory", 0)

    if inventory <= 0:
        return {
            "valid": False,
            "reason": "Selected product is out of stock.",
        }

    margin = candidate.get("margin", 0)
    minimum_margin = merchant_rules.get("min_margin", 0)

    if margin < minimum_margin:
        return {
            "valid": False,
            "reason": (
                f"Margin {margin:.2%} is below the required "
                f"minimum of {minimum_margin:.2%}."
            ),
        }

    return {
        "valid": True,
        "reason": "Decision passed all merchant guardrails.",
        "decision": decision,
        "candidate": candidate,
    }