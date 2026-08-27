import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# Reproducibility
random.seed(42)
np.random.seed(42)


# ============================================================
# 1. PRODUCT CATALOG
# ============================================================

products = [
    ("P001", "Wireless Headphones", "Audio", 2999, ["audio", "wireless"]),
    ("P002", "Headphone Case", "Accessories", 499, ["audio", "protection"]),
    ("P003", "USB-C Cable", "Accessories", 299, ["cable", "charging"]),
    ("P004", "Bluetooth Speaker", "Audio", 2499, ["audio", "wireless"]),
    ("P005", "Laptop", "Computers", 59999, ["computer", "work"]),
    ("P006", "Wireless Mouse", "Accessories", 999, ["computer", "mouse"]),
    ("P007", "Laptop Stand", "Accessories", 1499, ["computer", "ergonomics"]),
    ("P008", "USB-C Hub", "Accessories", 1999, ["computer", "connectivity"]),
    ("P009", "Mechanical Keyboard", "Accessories", 3499, ["computer", "keyboard"]),
    ("P010", "Webcam", "Accessories", 2999, ["computer", "camera"]),
    ("P011", "Smartphone", "Mobile", 29999, ["mobile", "electronics"]),
    ("P012", "Phone Case", "Accessories", 799, ["mobile", "protection"]),
    ("P013", "Screen Protector", "Accessories", 399, ["mobile", "protection"]),
    ("P014", "Power Bank", "Accessories", 1499, ["mobile", "charging"]),
    ("P015", "Wireless Charger", "Accessories", 1999, ["mobile", "charging"]),
    ("P016", "Smartwatch", "Wearables", 6999, ["wearable", "fitness"]),
    ("P017", "Smartwatch Strap", "Accessories", 799, ["wearable", "accessory"]),
    ("P018", "Fitness Band", "Wearables", 2999, ["wearable", "fitness"]),
    ("P019", "Running Shoes", "Fitness", 4999, ["fitness", "shoes"]),
    ("P020", "Yoga Mat", "Fitness", 1299, ["fitness", "yoga"]),
    ("P021", "Water Bottle", "Fitness", 699, ["fitness", "hydration"]),
    ("P022", "Coffee Maker", "Home", 4999, ["home", "coffee"]),
    ("P023", "Coffee Beans", "Home", 699, ["home", "coffee"]),
    ("P024", "Travel Mug", "Home", 999, ["home", "coffee"]),
    ("P025", "Backpack", "Lifestyle", 1999, ["travel", "bag"]),
    ("P026", "Travel Organizer", "Lifestyle", 799, ["travel", "organization"]),
    ("P027", "Sunglasses", "Lifestyle", 2499, ["fashion", "accessory"]),
    ("P028", "Desk Lamp", "Home", 1799, ["home", "desk"]),
    ("P029", "Notebook", "Stationery", 299, ["stationery", "writing"]),
    ("P030", "Pen Set", "Stationery", 199, ["stationery", "writing"]),
]


products_df = pd.DataFrame(
    products,
    columns=["product_id", "name", "category", "price", "tags"]
)

products_df["tags"] = products_df["tags"].apply(lambda x: ",".join(x))

# Random inventory
products_df["inventory"] = np.random.randint(10, 150, len(products_df))

# Synthetic cost price
products_df["cost_price"] = (
    products_df["price"]
    * np.random.uniform(0.50, 0.80, len(products_df))
).round(2)

# ============================================================
# 2. CUSTOMER PROFILES
# ============================================================

num_customers = 500

customers = []

age_segments = ["18-24", "25-34", "35-44", "45-54", "55+"]

for i in range(1, num_customers + 1):

    customer_id = f"C{i:03d}"

    age_segment = random.choice(age_segments)

    total_orders = max(
        1,
        int(np.random.poisson(6))
    )

    # Different customers have different spending levels
    spending_type = random.choice(
        ["low", "medium", "high"]
    )

    if spending_type == "low":
        average_order_value = np.random.normal(1500, 400)

    elif spending_type == "medium":
        average_order_value = np.random.normal(4000, 1000)

    else:
        average_order_value = np.random.normal(12000, 3000)

    average_order_value = max(500, round(average_order_value, 2))

    customers.append(
        [
            customer_id,
            age_segment,
            total_orders,
            average_order_value,
        ]
    )


customers_df = pd.DataFrame(
    customers,
    columns=[
        "customer_id",
        "age_segment",
        "total_orders",
        "average_order_value",
    ],
)


# ============================================================
# 3. REALISTIC PRODUCT RELATIONSHIPS
# ============================================================

# If a customer buys the key product,
# they are more likely to buy products in the list.

product_relationships = {

    "P001": ["P002", "P003", "P004"],      # Headphones
    "P005": ["P006", "P007", "P008", "P009", "P010"],  # Laptop
    "P011": ["P012", "P013", "P014", "P015"],           # Smartphone
    "P016": ["P017", "P018"],               # Smartwatch
    "P019": ["P020", "P021"],               # Running Shoes
    "P022": ["P023", "P024"],               # Coffee Maker
    "P025": ["P026", "P027"],               # Backpack
    "P029": ["P030"],                        # Notebook
}


# ============================================================
# 4. GENERATE TRANSACTIONS
# ============================================================

num_transactions = 7000

product_ids = products_df["product_id"].tolist()

transactions = []

start_date = datetime(2025, 1, 1)

for i in range(1, num_transactions + 1):

    customer = random.choice(customers_df.to_dict("records"))

    customer_id = customer["customer_id"]

    # Select a primary product
    primary_product = random.choice(product_ids)

    transaction_date = start_date + timedelta(
        days=random.randint(0, 365)
    )

    transaction_id = f"T{i:05d}"

    transactions.append(
        [
            transaction_id,
            customer_id,
            primary_product,
            transaction_date.strftime("%Y-%m-%d"),
            1,
        ]
    )

    # Occasionally add a complementary product
    if primary_product in product_relationships:

        related_products = product_relationships[primary_product]

        # 35% probability of buying a complementary product
        if random.random() < 0.35:

            complementary_product = random.choice(
                related_products
            )

            transactions.append(
                [
                    transaction_id,
                    customer_id,
                    complementary_product,
                    transaction_date.strftime("%Y-%m-%d"),
                    1,
                ]
            )


transactions_df = pd.DataFrame(
    transactions,
    columns=[
        "transaction_id",
        "customer_id",
        "product_id",
        "date",
        "quantity",
    ],
)


# ============================================================
# 5. SAVE DATA
# ============================================================

products_df.to_csv(
    "data/products.csv",
    index=False
)

customers_df.to_csv(
    "data/customers.csv",
    index=False
)

transactions_df.to_csv(
    "data/transactions.csv",
    index=False
)


# ============================================================
# 6. SUMMARY
# ============================================================

print("Synthetic data generated successfully!")
print()
print(f"Products     : {len(products_df)}")
print(f"Customers    : {len(customers_df)}")
print(f"Transactions : {len(transactions_df)}")
print()

print("Files created:")
print("data/products.csv")
print("data/customers.csv")
print("data/transactions.csv")