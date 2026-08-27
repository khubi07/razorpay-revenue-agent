from openai import OpenAI


client = OpenAI()


def run_agent(context):

    prompt = f"""
You are a revenue-growth agent for a merchant.

Your job is to evaluate the provided recommendation
candidate and explain the recommended action.

You must follow these rules:

1. Only recommend the provided candidate.
2. Never invent products or prices.
3. Do not execute payments.
4. Customer approval is always required.
5. If the candidate is None, recommend doing nothing.

Merchant context:

{context}

Return:

Action:
Reason:
Customer approval required:
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":

    context = {
        "cart": [
            {
                "product_id": "P001",
                "product_name": "Wireless Headphones",
                "price": 2999
            }
        ],

        "recommendation": {
            "product_id": "P003",
            "product_name": "USB-C Cable",
            "price": 299,
            "acceptance_probability": 0.707,
            "expected_revenue": 211.40
        },

        "merchant_rules": {
            "minimum_margin_percentage": 0.20,
            "allowed_actions": [
                "cross_sell",
                "upsell"
            ]
        }
    }

    result = run_agent(context)

    print("===== AI AGENT =====")
    print(result)