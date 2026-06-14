from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.core.security import get_current_active_user

router = APIRouter(tags=["Subscriptions"])

# Plan quotas & prices
quotas = {
    "starter": {"analyses": 10, "pages": 10},
    "pro": {"analyses": 100, "pages": -1},
    "enterprise": {"analyses": -1, "pages": -1},
}

prices = {"starter": 19, "pro": 49, "enterprise": 99}

@router.post("/create", response_model=SubscriptionResponse)
async def create_subscription(
    sub_in: SubscriptionCreate,
    current_user: User = Depends(get_current_active_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    now = datetime.now()
    period_end = now + timedelta(days=30 if sub_in.billing_cycle == "monthly" else 365)

    subscription = Subscription(
        user_id=str(current_user.id),
        plan=sub_in.plan_id,
        billing_cycle=sub_in.billing_cycle,
        price=prices[sub_in.plan_id],
        currency="EUR",
        status="active",
        current_period_start=now,
        current_period_end=period_end,
        analyses_limit=quotas[sub_in.plan_id]["analyses"],
        pages_per_analysis_limit=quotas[sub_in.plan_id]["pages"],
        analyses_used=0,
        customer_info=sub_in.customer_info
    )

    try:
        await subscription.insert()  # Save subscription
        current_user.plan = sub_in.plan_id  # Update user plan
        await current_user.save()
    except Exception as e:
        print("Subscription save failed:", e)
        raise HTTPException(status_code=500, detail="Database error: " + str(e))

    return {
        "subscription_id": str(subscription.id),
        "plan_id": sub_in.plan_id,
        "status": "active",
        "message": "✅ Subscription activated successfully"
    }

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(current_user: User = Depends(get_current_active_user)):
    sub = await Subscription.find_one(Subscription.user_id == str(current_user.id))
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return {
        "subscription_id": str(sub.id),
        "plan_id": sub.plan,
        "status": sub.status,
        "message": "Subscription loaded successfully"
    }
