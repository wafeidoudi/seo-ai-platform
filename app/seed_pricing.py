import asyncio
from datetime import datetime
from app.models.pricing import PricingPlan
from app.core.database import init_db

async def seed_pricing():
    await init_db()
    
    default_plans = [
        {
            "name": "starter",
            "display_name": "Starter",
            "description": "Perfect for small projects",
            "price_monthly": 19,
            "price_yearly": 190,
            "discount_percentage": 20,
            "features": ["10 analyses", "10 pages per analysis", "Community support"],
            "is_active": True,
            "is_popular": False,
            "order": 1
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "description": "Best for freelancers",
            "price_monthly": 49,
            "price_yearly": 490,
            "discount_percentage": 20,
            "features": ["100 analyses", "Unlimited pages per analysis", "Priority support", "Advanced recommendations"],
            "is_active": True,
            "is_popular": True,
            "order": 2
        },
        {
            "name": "enterprise",
            "display_name": "Enterprise",
            "description": "For agencies & teams",
            "price_monthly": 99,
            "price_yearly": 990,
            "discount_percentage": 20,
            "features": ["Unlimited analyses", "Unlimited pages", "Team collaboration", "Dedicated support"],
            "is_active": True,
            "is_popular": False,
            "order": 3
        }
    ]
    
    for plan_data in default_plans:
        existing = await PricingPlan.find_one(PricingPlan.name == plan_data["name"])
        if not existing:
            plan = PricingPlan(**plan_data)
            await plan.insert()
            print(f"✅ Created plan: {plan_data['name']}")
        else:
            print(f"⏭️ Plan already exists: {plan_data['name']}")

if __name__ == "__main__":
    asyncio.run(seed_pricing())