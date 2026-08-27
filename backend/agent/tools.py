import pandas as pd


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


if __name__ == "__main__":

    result = get_customer_context("C002")

    print("===== CUSTOMER CONTEXT =====")
    print(result)