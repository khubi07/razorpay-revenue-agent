import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
from revenue_pipeline import run_revenue_pipeline


TRANSACTIONS_PATH = "data/transactions.csv"
CUSTOMERS_PATH = "data/customers.csv"


def get_customer_context(customer_id):
    transactions = pd.read_csv(TRANSACTIONS_PATH)
    customers = pd.read_csv(CUSTOMERS_PATH)

    customer = customers[
        customers["customer_id"] == customer_id
    ]

    if customer.empty:
        return {
            "error": f"Customer {customer_id} not found."
        }

    customer_transactions = transactions[
        transactions["customer_id"] == customer_id
    ]

    products_purchased = (
        customer_transactions["product_id"]
        .unique()
        .tolist()
    )

    return {
        "customer_id": customer_id,
        "total_orders": int(customer["total_orders"].iloc[0]),
        "average_order_value": float(
            customer["average_order_value"].iloc[0]
        ),
        "products_already_purchased": products_purchased
    }

def get_recommendations(customer_id, cart_product_ids):
    """
    Get the best revenue-growth recommendation
    for a customer and their current cart.
    """

    return run_revenue_pipeline(
        customer_id=customer_id,
        cart_product_ids=cart_product_ids
    )

def get_merchant_rules():
    return {
        "minimum_margin_percentage": 0.20,
        "max_discount": 0.10,
        "max_incentive": 500,
        "allowed_actions": [
            "cross_sell",
            "upsell"
        ]
    }


if __name__ == "__main__":

    customer_id = "C002"
    cart = ["P001"]

    print("===== CUSTOMER CONTEXT =====")
    print(get_customer_context(customer_id))

    print("\n===== RECOMMENDATION =====")
    recommendation = get_recommendations(customer_id, cart)

    print("RESULT FROM TOOL:")
    print(recommendation)   

    print("\n===== MERCHANT RULES =====")
    print(get_merchant_rules())