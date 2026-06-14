from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from app.models.pricing import PricingPlan, PricingOffer
from app.schemas.pricing import (
    PricingPlanCreate, PricingPlanUpdate, PricingPlanResponse,
    PricingOfferCreate, PricingOfferUpdate, PricingOfferResponse
)
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/pricing", tags=["💰 Pricing Management"])

# ==================== PLANS ====================

@router.get("/plans", response_model=List[PricingPlanResponse])
async def get_all_plans(current_user: User = Depends(get_current_active_user)):
    plans = await PricingPlan.find_all().sort(+PricingPlan.order).to_list()
    return [PricingPlanResponse(
        id=str(plan.id), name=plan.name, display_name=plan.display_name,
        description=plan.description, price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly, discount_percentage=plan.discount_percentage,
        features=plan.features, is_active=plan.is_active, is_popular=plan.is_popular,
        order=plan.order, created_at=plan.created_at, updated_at=plan.updated_at
    ) for plan in plans]

@router.get("/plans/public", response_model=List[PricingPlanResponse])
async def get_public_plans():
    plans = await PricingPlan.find(PricingPlan.is_active == True).sort(+PricingPlan.order).to_list()
    return [PricingPlanResponse(
        id=str(plan.id), name=plan.name, display_name=plan.display_name,
        description=plan.description, price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly, discount_percentage=plan.discount_percentage,
        features=plan.features, is_active=plan.is_active, is_popular=plan.is_popular,
        order=plan.order, created_at=plan.created_at, updated_at=plan.updated_at
    ) for plan in plans]

@router.post("/plans", response_model=PricingPlanResponse, status_code=201)
async def create_plan(plan_in: PricingPlanCreate, admin: User = Depends(get_current_admin_user)):
    existing = await PricingPlan.find_one(PricingPlan.name == plan_in.name)
    if existing:
        raise HTTPException(400, "Plan with this name already exists")
    
    plan = PricingPlan(**plan_in.dict())
    await plan.insert()
    
    return PricingPlanResponse(
        id=str(plan.id), name=plan.name, display_name=plan.display_name,
        description=plan.description, price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly, discount_percentage=plan.discount_percentage,
        features=plan.features, is_active=plan.is_active, is_popular=plan.is_popular,
        order=plan.order, created_at=plan.created_at, updated_at=plan.updated_at
    )

@router.put("/plans/{plan_id}", response_model=PricingPlanResponse)
async def update_plan(plan_id: str, plan_in: PricingPlanUpdate, admin: User = Depends(get_current_admin_user)):
    plan = await PricingPlan.get(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    
    update_data = plan_in.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    await plan.save()
    
    return PricingPlanResponse(
        id=str(plan.id), name=plan.name, display_name=plan.display_name,
        description=plan.description, price_monthly=plan.price_monthly,
        price_yearly=plan.price_yearly, discount_percentage=plan.discount_percentage,
        features=plan.features, is_active=plan.is_active, is_popular=plan.is_popular,
        order=plan.order, created_at=plan.created_at, updated_at=plan.updated_at
    )

@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan(plan_id: str, admin: User = Depends(get_current_admin_user)):
    plan = await PricingPlan.get(plan_id)
    if not plan:
        raise HTTPException(404, "Plan not found")
    await plan.delete()

# ==================== OFFERS ====================

@router.get("/offers", response_model=List[PricingOfferResponse])
async def get_all_offers(admin: User = Depends(get_current_admin_user)):
    offers = await PricingOffer.find_all().sort(-PricingOffer.created_at).to_list()
    return [PricingOfferResponse(
        id=str(offer.id), code=offer.code, name=offer.name,
        description=offer.description, discount_percentage=offer.discount_percentage,
        applicable_plans=offer.applicable_plans, valid_from=offer.valid_from,
        valid_until=offer.valid_until, max_uses=offer.max_uses,
        used_count=offer.used_count, is_active=offer.is_active,
        created_at=offer.created_at
    ) for offer in offers]

@router.post("/offers", response_model=PricingOfferResponse, status_code=201)
async def create_offer(offer_in: PricingOfferCreate, admin: User = Depends(get_current_admin_user)):
    existing = await PricingOffer.find_one(PricingOffer.code == offer_in.code)
    if existing:
        raise HTTPException(400, "Offer code already exists")
    
    offer = PricingOffer(**offer_in.dict())
    await offer.insert()
    
    return PricingOfferResponse(
        id=str(offer.id), code=offer.code, name=offer.name,
        description=offer.description, discount_percentage=offer.discount_percentage,
        applicable_plans=offer.applicable_plans, valid_from=offer.valid_from,
        valid_until=offer.valid_until, max_uses=offer.max_uses,
        used_count=offer.used_count, is_active=offer.is_active,
        created_at=offer.created_at
    )

@router.put("/offers/{offer_id}", response_model=PricingOfferResponse)
async def update_offer(offer_id: str, offer_in: PricingOfferUpdate, admin: User = Depends(get_current_admin_user)):
    offer = await PricingOffer.get(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    
    update_data = offer_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offer, field, value)
    
    await offer.save()
    
    return PricingOfferResponse(
        id=str(offer.id), code=offer.code, name=offer.name,
        description=offer.description, discount_percentage=offer.discount_percentage,
        applicable_plans=offer.applicable_plans, valid_from=offer.valid_from,
        valid_until=offer.valid_until, max_uses=offer.max_uses,
        used_count=offer.used_count, is_active=offer.is_active,
        created_at=offer.created_at
    )

@router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(offer_id: str, admin: User = Depends(get_current_admin_user)):
    offer = await PricingOffer.get(offer_id)
    if not offer:
        raise HTTPException(404, "Offer not found")
    await offer.delete()