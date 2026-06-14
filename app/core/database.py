from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.models.analysis import Analysis
from app.models.prompt_config import PromptConfig
from app.models.pricing import PricingPlan, PricingOffer
from app.models.password_reset import PasswordResetToken

client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]  # ✅ AJOUTÉ pour auth.py

async def init_db():
    await init_beanie(
        database=db,
        document_models=[
            User,
            Subscription,
            Analysis,
            PromptConfig,
            PricingPlan,
            PricingOffer, PasswordResetToken
        ]
    )
    print("✅ MongoDB connecté avec Beanie")
    print(f"📊 Base de données: {settings.DATABASE_NAME}")

