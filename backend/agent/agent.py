import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import (
    get_customer_context,
    get_recommendations,
    get_merchant_rules
)


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

key = os.getenv("OPENROUTER_API_KEY")

print("API key loaded:", bool(key))


def run_agent(customer_id, cart_product_ids):

    customer_context = get_customer_context(
        customer_id
    )

    recommendations = get_recommendations(
        customer_id,
        cart_product_ids
    )

    merchant_rules = get_merchant_rules()

    context = {
        "customer": customer_context,
        "recommendation_engine": recommendations,
        "merchant_rules": merchant_rules
    }

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": """
You are a revenue-growth agent for a merchant.

Your job is to evaluate the output of the
merchant's recommendation engine and decide
the next revenue-growth action.

Rules:

1. Never invent products or prices.
2. Never override merchant rules.
3. Prefer the recommendation engine's
   validated candidate.
4. You may choose:
   - cross_sell
   - upsell
   - do_nothing
5. Money-affecting actions require
   customer approval.
6. If there is no valid recommendation,
   choose do_nothing.
7. Give a short explanation for your decision.

Return JSON with:

{
    "action": "...",
    "product_id": "... or null",
    "reason": "..."
}
"""
            },
            {
                "role": "user",
                "content": json.dumps(context)
            }
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    result = run_agent(
        customer_id="C002",
        cart_product_ids=["P001"]
    )

    print("\n===== LLM AGENT =====")
    print(result)