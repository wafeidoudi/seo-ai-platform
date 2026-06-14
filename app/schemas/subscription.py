from pydantic import BaseModel
from typing import Optional, Literal, Dict

class SubscriptionCreate(BaseModel):
    plan_id: Literal["starter", "pro", "enterprise"]
    billing_cycle: Literal["monthly", "yearly"]
    customer_info: Optional[Dict] = None

class SubscriptionResponse(BaseModel):
    subscription_id: Optional[str] = None
    plan_id: str
    status: Optional[str] = None
    message: Optional[str] = None

    class Config:
        from_attributes = True