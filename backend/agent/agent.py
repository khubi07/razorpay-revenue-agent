import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from tools import (
    get_customer_context,
    get_recommendations,
    get_merchant_rules
)


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(key))

get_customer_context_tool = {
    "name": "get_customer_context",
    "description": "Get customer purchase history and spending information.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer's ID."
            }
        },
        "required": ["customer_id"]
    }
}

def execute_tool(function_name, arguments):
    if function_name == "get_customer_context":
        return get_customer_context(
            arguments["customer_id"]
        )

    return {
        "error": f"Unknown tool: {function_name}"
    }

def run_agent(customer_id, cart_product_ids):

    
    context = {
    "customer_id": customer_id,
    "cart_product_ids": cart_product_ids
    }
    response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        {
            "role": "user",
            "parts": [
                {
                    "text": """
You are a revenue-growth agent for a merchant.

Your job is to evaluate the merchant's
recommendation engine and customer context.

Rules:
1. Never invent products or prices.
2. Never override merchant rules.
3. Prefer validated recommendations.
4. You may choose:
   - cross_sell
   - upsell
   - do_nothing
5. Money-affecting actions require customer approval.
6. If there is no valid recommendation,
   choose do_nothing.
7. Give a short explanation.

Customer and recommendation data:

"""
                },
                {
                    "text": json.dumps(context)
                }
            ]
        }
    ],
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="get_customer_context",
                        description="Get customer purchase history and spending information.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "customer_id": types.Schema(
                                    type=types.Type.STRING,
                                    description="The customer's ID."
                                )
                            },
                            required=["customer_id"]
                        )
                    )
                ]
            )
        ]
    )
)

    if not response.candidates:
        print("No response candidates returned.")
        return None

    content = response.candidates[0].content

    if not content or not content.parts:
        print("No response parts returned.")
        return None

    for part in content.parts:

        if part.function_call:
            function_call = part.function_call

            print("\n===== TOOL REQUESTED BY GEMINI =====")
            print("Tool:", function_call.name)
            print("Arguments:", function_call.args)

            result = execute_tool(
                function_call.name,
                function_call.args
            )

            print("\n===== TOOL RESULT =====")
            print(result)

if __name__ == "__main__":

    result = run_agent(
        customer_id="C002",
        cart_product_ids=["P001"]
    )

    print("\n===== LLM AGENT =====")
    print(result)