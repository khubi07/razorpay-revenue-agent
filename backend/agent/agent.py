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

    recommendations = None
    merchant_rules = None

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
Return ONLY valid JSON:
    {{
        "action": "cross_sell | upsell | do_nothing",
        "product_id": "product ID or null",
        "reason": "short explanation"
    }}
"""
                )
            ]
        )
    ]

        # ========================================================
    # AGENT LOOP
    # ========================================================

    recommendations = None
    merchant_rules = None

    while True:

        # ----------------------------------------------------
        # Ask Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                tools=gemini_tools,
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "action": types.Schema(
                            type=types.Type.STRING
                        ),
                        "product_id": types.Schema(
                            type=types.Type.STRING,
                            nullable=True
                        ),
                        "reason": types.Schema(
                            type=types.Type.STRING
                        )
                    },
                    required=[
                        "action",
                        "product_id",
                        "reason"
                    ]
                )
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
        # Check whether Gemini requested tools
        # ----------------------------------------------------

        tool_calls = [
            part.function_call
            for part in content.parts
            if part.function_call
        ]

        if tool_calls:

            # Append Gemini's function-call message exactly once.
            contents.append(content)

            for function_call in tool_calls:

                if not function_call.name:
                    print("Tool call has no function name.")
                    continue

                function_name = function_call.name
                arguments = dict(function_call.args or {})

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

                if function_name == "get_recommendations":
                    recommendations = result

                elif function_name == "get_merchant_rules":
                    merchant_rules = result

                print("\n===== TOOL RESULT =====")
                print(result)

                # Append the corresponding function response.
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

            # Ask Gemini again after all tool responses.
            continue

        # ----------------------------------------------------
        # Final Gemini response
        # ----------------------------------------------------

        print("\n===== FINAL GEMINI RESPONSE =====")

        final_text = None

        for part in content.parts:
            if part.text:
                final_text = part.text
                break

        if not final_text:
            print("Gemini returned no final text response.")
            return None

        print(final_text)

        try:
            decision = json.loads(final_text)

        except json.JSONDecodeError:
            print("Gemini returned invalid JSON.")
            return {
                "valid": False,
                "reason": "Gemini returned invalid JSON."
            }

        # These are fallback calls only. Normally both values
        # were already collected through Gemini's tool calls.
        if recommendations is None:
            recommendations = get_recommendations(
                customer_id,
                cart_product_ids
            )

        if merchant_rules is None:
            merchant_rules = get_merchant_rules()

        validated_result = validate_agent_decision(
            decision=decision,
            recommendations=recommendations,
            merchant_rules=merchant_rules
        )

        print("\n===== VALIDATED AGENT DECISION =====")
        print(json.dumps(validated_result, indent=2))

        return validated_result

def validate_agent_decision(decision, recommendations, merchant_rules):

    # --------------------------------------------------------
    # 1. Validate action
    # --------------------------------------------------------

    allowed_actions = merchant_rules.get(
        "allowed_actions",
        []
    )

    action = decision.get("action")

    if action == "do_nothing":
        return {
            "valid": True,
            "decision": {
                "action": "do_nothing",
                "product_id": None,
                "reason": decision.get(
                    "reason",
                    "No suitable recommendation was available."
                )
            }
        }

    if action not in allowed_actions:
        return {
            "valid": False,
            "reason": "Action is not allowed by merchant rules."
        }

    # --------------------------------------------------------
    # 2. Validate product ID
    # --------------------------------------------------------

    product_id = decision.get("product_id")

    if not product_id:
        return {
            "valid": False,
            "reason": "Revenue action requires a product_id."
        }

    # --------------------------------------------------------
    # 3. Make sure product exists in validated recommendation
    # --------------------------------------------------------

    recommended_candidate = recommendations.get("candidate")

    if not recommended_candidate:
        return {
            "valid": False,
            "reason": "No validated recommendation exists."
        }

    if product_id != recommended_candidate.get("product_id"):
        return {
            "valid": False,
            "reason": "LLM selected a product different from the validated recommendation."
        }

    # --------------------------------------------------------
    # 4. Validate action type
    # --------------------------------------------------------

    if action != recommended_candidate.get("action_type"):
        return {
            "valid": False,
            "reason": "LLM action does not match the validated recommendation."
        }

    # --------------------------------------------------------
    # 5. Validate inventory
    # --------------------------------------------------------

    if recommended_candidate.get("inventory", 0) <= 0:
        return {
            "valid": False,
            "reason": "Recommended product is out of stock."
        }

    # --------------------------------------------------------
    # 6. Validate margin
    # --------------------------------------------------------

    price = recommended_candidate.get("price", 0)
    cost_price = recommended_candidate.get("cost_price", 0)

    if price <= 0:
        return {
            "valid": False,
            "reason": "Invalid product price."
        }

    profit = price - cost_price
    margin = profit / price

    minimum_margin = merchant_rules.get(
        "minimum_margin_percentage",
        0
    )

    if margin < minimum_margin:
        return {
            "valid": False,
            "reason": "Product margin is below merchant minimum."
        }

    # --------------------------------------------------------
    # Everything passed
    # --------------------------------------------------------

    return {
        "valid": True,
        "decision": decision
    }
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