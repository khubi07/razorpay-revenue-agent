import pandas as pd
import numpy as np


# Load existing products
products = pd.read_csv(
    "data/products.csv"
)


# Generate synthetic cost price
products["cost_price"] = (
    products["price"]
    * np.random.uniform(
        0.50,
        0.80,
        len(products)
    )
).round(2)


# Save updated products
products.to_csv(
    "data/products.csv",
    index=False
)


print("Cost price added successfully!")

print(
    products[
        [
            "product_id",
            "name",
            "price",
            "cost_price"
        ]
    ].to_string(index=False)
)