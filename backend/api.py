from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.agent.agent import run_agent

app = FastAPI()
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