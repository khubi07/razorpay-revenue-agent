from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.agent.agent import get_recommendations, run_agent
import os
import razorpay
from dotenv import load_dotenv
from fastapi import HTTPException
from backend.revenue_pipeline import get_cart_revenue

app = FastAPI()

load_dotenv()

razorpay_client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID"),
        os.getenv("RAZORPAY_KEY_SECRET"),
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecommendationRequest(BaseModel):
    customer_id: str
    cart_product_ids: list[str]


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Razorpay Revenue Agent API is running"
    }


@app.post("/recommend")
def recommend(request: RecommendationRequest):
    try:
        return run_agent(
            customer_id=request.customer_id,
            cart_product_ids=request.cart_product_ids,
        )
    except Exception as error:
        return {
            "status": "error",
            "message": str(error),
        }

@app.post("/create-order")
def create_order():
    try:
        order = razorpay_client.order.create(
            data={
                "amount": 29900,
                "currency": "INR",
                "receipt": "p003_cross_sell_001",
                "notes": {
                    "product_id": "P003",
                    "customer_id": "C002",
                    "source": "revenue_agent",
                },
            }
        )

        return {
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key_id": os.getenv("RAZORPAY_KEY_ID"),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@app.post("/verify-payment")
def verify_payment(request: PaymentVerificationRequest):
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": request.razorpay_order_id,
            "razorpay_payment_id": request.razorpay_payment_id,
            "razorpay_signature": request.razorpay_signature,
        })

        return {
            "valid": True,
            "message": "Payment verified successfully",
            "payment_id": request.razorpay_payment_id,
            "order_id": request.razorpay_order_id,
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Payment verification failed",
        )

@app.get("/experiment")
def experiment():
    customer_id = "C002"
    cart_product_ids = ["P001"]

    without_agent_revenue = get_cart_revenue(cart_product_ids)

    agent_result = run_agent(
        customer_id=customer_id,
        cart_product_ids=cart_product_ids,
    )

    decision = agent_result.get("decision")

    expected_incremental_revenue = 0.0

    if decision:
        recommendation_result = get_recommendations(
            customer_id=customer_id,
            cart_product_ids=cart_product_ids,
        )

        selected_product_id = decision.get("product_id")

        selected_candidate = recommendation_result.get("candidate")

        if (
            selected_candidate
            and selected_candidate.get("product_id") != selected_product_id
        ):
            selected_candidate = None

        if selected_candidate:
            expected_incremental_revenue = (
                float(selected_candidate["price"])
                * float(selected_candidate["acceptance_probability"])
            )

    with_agent_expected_revenue = (
        without_agent_revenue
        + expected_incremental_revenue
    )

    revenue_lift = (
        with_agent_expected_revenue
        - without_agent_revenue
    )

    revenue_lift_percent = (
        (revenue_lift / without_agent_revenue) * 100
        if without_agent_revenue > 0
        else 0
    )

    return {
        "customer_id": customer_id,
        "cart_product_ids": cart_product_ids,
        "without_agent_revenue": round(without_agent_revenue, 2),
        "with_agent_expected_revenue": round(
            with_agent_expected_revenue,
            2,
        ),
        "expected_incremental_revenue": round(
            expected_incremental_revenue,
            2,
        ),
        "revenue_lift": round(revenue_lift, 2),
        "revenue_lift_percent": round(
            revenue_lift_percent,
            2,
        ),
        "agent_decision": decision,
        "agent_decision_valid": agent_result.get("valid"),
    }