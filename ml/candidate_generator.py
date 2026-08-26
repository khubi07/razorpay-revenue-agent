import pandas as pd
from itertools import combinations
from collections import Counter


class CandidateGenerator:

    def __init__(self, transactions_path, products_path):

        self.transactions = pd.read_csv(transactions_path)
        self.products = pd.read_csv(products_path)

        self.product_names = dict(
            zip(
                self.products["product_id"],
                self.products["name"]
            )
        )

        self.inventory = dict(
            zip(
                self.products["product_id"],
                self.products["inventory"]
            )
        )

        self.co_purchase_counts = self._build_co_purchase_counts()

    # ========================================================
    # BUILD CO-PURCHASE COUNTS
    # ========================================================

    def _build_co_purchase_counts(self):

        pair_counts = Counter()

        for transaction_id, group in self.transactions.groupby(
            "transaction_id"
        ):

            products = group["product_id"].unique()

            for pair in combinations(sorted(products), 2):
                pair_counts[pair] += 1

        return pair_counts

    # ========================================================
    # GET PRODUCTS ALREADY PURCHASED BY CUSTOMER
    # ========================================================

    def _get_customer_products(self, customer_id):

        customer_transactions = self.transactions[
            self.transactions["customer_id"] == customer_id
        ]

        return set(
            customer_transactions["product_id"]
        )

    # ========================================================
    # GENERATE FILTERED CANDIDATES
    # ========================================================

    def get_candidates(
        self,
        product_id,
        customer_id,
        cart_product_ids=None,
        top_k=5
    ):

        if cart_product_ids is None:
            cart_product_ids = []

        cart_product_ids = set(cart_product_ids)

        customer_products = self._get_customer_products(
            customer_id
        )

        candidates = []

        # Find products bought together with product_id
        for (product_a, product_b), count in self.co_purchase_counts.items():

            if product_a == product_id:
                candidate_id = product_b

            elif product_b == product_id:
                candidate_id = product_a

            else:
                continue

            # ================================================
            # FILTER 1: Already in cart
            # ================================================

            if candidate_id in cart_product_ids:
                continue

            # ================================================
            # FILTER 2: Customer already owns product
            # ================================================

            if candidate_id in customer_products:
                continue

            # ================================================
            # FILTER 3: Out of stock
            # ================================================

            if self.inventory.get(candidate_id, 0) <= 0:
                continue

            candidates.append(
                (candidate_id, count)
            )

        # Highest co-purchase count first
        candidates.sort(
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for candidate_id, count in candidates[:top_k]:

            results.append(
                {
                    "product_id": candidate_id,
                    "product_name": self.product_names[candidate_id],
                    "co_purchase_count": count,
                    "inventory": self.inventory[candidate_id]
                }
            )

        return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    generator = CandidateGenerator(
        "data/transactions.csv",
        "data/products.csv"
    )

    customer_id = "C002"

    cart = ["P001"]

    candidates = generator.get_candidates(
        product_id="P001",
        customer_id=customer_id,
        cart_product_ids=cart,
        top_k=5
    )

    print("Filtered candidates:")
    print()

    for candidate in candidates:
        print(candidate)