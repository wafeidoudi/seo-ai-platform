from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class PlanFeatureUpdate(BaseModel):
    name: str
    included: bool = True

class PricingPlanCreate(BaseModel):
    name: str
    display_name: str
    description: str
    price_monthly: float = Field(..., ge=0)
    price_yearly: float = Field(..., ge=0)
    discount_percentage: int = Field(default=0, ge=0, le=100)
    features: List[str] = []
    is_active: bool = True
    is_popular: bool = False
    order: int = 0

class PricingPlanUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = Field(None, ge=0)
    price_yearly: Optional[float] = Field(None, ge=0)
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    features: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_popular: Optional[bool] = None
    order: Optional[int] = None

class PricingPlanResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: str
    price_monthly: float
    price_yearly: float
    discount_percentage: int
    features: List[str]
    is_active: bool
    is_popular: bool
    order: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class PricingOfferCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    discount_percentage: int = Field(..., ge=0, le=100)
    applicable_plans: List[str] = []
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int] = None

class PricingOfferUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    discount_percentage: Optional[int] = Field(None, ge=0, le=100)
    applicable_plans: Optional[List[str]] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    is_active: Optional[bool] = None

class PricingOfferResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    discount_percentage: int
    applicable_plans: List[str]
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int]
    used_count: int
    is_active: bool
    created_at: datetime