from beanie import Document, Indexed
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class PlanFeature(BaseModel):
    name: str
    included: bool = True

class PricingPlan(Document):
    """Modèle pour les plans de prix dynamiques"""
    name: Indexed(str, unique=True)  # starter, pro, enterprise
    display_name: str
    description: str
    price_monthly: float = Field(..., ge=0)
    price_yearly: float = Field(..., ge=0)
    discount_percentage: int = Field(default=0, ge=0, le=100)  # réduction affichée
    features: List[str] = []
    is_active: bool = True
    is_popular: bool = False
    order: int = 0  # ordre d'affichage
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Settings:
        name = "pricing_plans"
        use_state_management = True

class PricingOffer(Document):
    """Offres promotionnelles"""
    code: Indexed(str, unique=True)  # code promo
    name: str
    description: Optional[str] = None
    discount_percentage: int = Field(..., ge=0, le=100)
    applicable_plans: List[str] = []  # ["starter", "pro"] ou [] pour tous
    valid_from: datetime
    valid_until: datetime
    max_uses: Optional[int] = None
    used_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "pricing_offers"
        use_state_management = True