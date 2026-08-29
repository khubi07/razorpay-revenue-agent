import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

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


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(key))

if not key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(
    api_key=key
)


# ============================================================
# GEMINI TOOL DEFINITION
# ============================================================

get_customer_context_tool = types.FunctionDeclaration(
    name="get_customer_context",
    description=(
        "Get customer purchase history and spending information."
    ),
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

get_recommendations_tool = types.FunctionDeclaration(
    name="get_recommendations",
    description=(
        "Get validated product recommendations for a customer "
        "based on their cart and purchase history."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "customer_id": types.Schema(
                type=types.Type.STRING,
                description="The customer's ID."
            ),
            "cart_product_ids": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING
                ),
                description="Product IDs currently in the customer's cart."
            )
        },
        required=[
            "customer_id",
            "cart_product_ids"
        ]
    )
)


get_merchant_rules_tool = types.FunctionDeclaration(
    name="get_merchant_rules",
    description=(
        "Get the merchant's revenue, margin, discount, "
        "incentive, and allowed-action rules."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={}
    )
)


# Keep all available tools together
gemini_tools = [
    types.Tool(
        function_declarations=[
            get_customer_context_tool,
            get_recommendations_tool,
            get_merchant_rules_tool
        ]
    )
]


# ============================================================
# TOOL EXECUTOR
# ============================================================

def execute_tool(function_name, arguments):

    if function_name == "get_customer_context":

        return get_customer_context(
            arguments["customer_id"]
        )

    if function_name == "get_recommendations":

        return get_recommendations(
            arguments["customer_id"],
            arguments["cart_product_ids"]
        )

    if function_name == "get_merchant_rules":

        return get_merchant_rules()

    return {
        "error": f"Unknown tool: {function_name}"
    }


# ============================================================
# AGENT
# ============================================================

def run_agent(customer_id, cart_product_ids):

    context = {
        "customer_id": customer_id,
        "cart_product_ids": cart_product_ids
    }

    # --------------------------------------------------------
    # Initial user message
    # --------------------------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
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

Customer and cart information:

{json.dumps(context)}

Use the available tools whenever you need information
that is not already provided.

You should obtain:
- customer context when needed
- validated recommendations before making a recommendation
- merchant rules before making a revenue decision

Never invent missing information.
"""
                )
            ]
        )
    ]

    # ========================================================
    # AGENT LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # Ask Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=gemini_tools
            )
        )

        # ----------------------------------------------------
        # Validate response
        # ----------------------------------------------------

        if not response.candidates:
            print("No response candidates returned.")
            return None

        content = response.candidates[0].content

        if not content or not content.parts:
            print("No response parts returned.")
            return None

        # ----------------------------------------------------
        # Check whether Gemini requested a tool
        # ----------------------------------------------------

        tool_called = False

        for part in content.parts:

            if not part.function_call:
                continue

            tool_called = True

            function_call = part.function_call

            # ------------------------------------------------
            # Validate function name
            # ------------------------------------------------

            if not function_call.name:
                print("Tool call has no function name.")
                continue

            function_name = function_call.name
            arguments = function_call.args or {}

            print("\n===== TOOL REQUESTED BY GEMINI =====")
            print("Tool:", function_name)
            print("Arguments:", arguments)

            # ------------------------------------------------
            # Execute Python tool
            # ------------------------------------------------

            result = execute_tool(
                function_name,
                arguments
            )

            print("\n===== TOOL RESULT =====")
            print(result)

            # ------------------------------------------------
            # Add Gemini's function-call message to history
            # ------------------------------------------------

            contents.append(content)

            # ------------------------------------------------
            # Add tool result to conversation
            # ------------------------------------------------

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_function_response(
                            name=function_name,
                            response={
                                "result": result
                            }
                        )
                    ]
                )
            )

        # ----------------------------------------------------
        # If Gemini did not request a tool,
        # we have the final answer.
        # ----------------------------------------------------

        if not tool_called:

            print("\n===== FINAL GEMINI RESPONSE =====")
            print(response.text)

            return response.text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = run_agent(
        customer_id="C002",
        cart_product_ids=["P001"]
    )

    print("\n===== LLM AGENT =====")
    print(result)