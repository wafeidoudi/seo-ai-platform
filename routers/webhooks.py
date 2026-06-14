# backend/app/routers/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Header
from app.models.subscription import Subscription
from app.models.user import User
import stripe

router = APIRouter(prefix="/api/webhooks", tags=["🔔 Webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """Webhook pour recevoir les événements Stripe"""
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Signature invalide")
    
    # Gérer l'événement "checkout.session.completed"
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Mettre à jour l'utilisateur
        user = await User.get(session["metadata"]["user_id"])
        if user:
            user.plan = session["metadata"]["plan_id"]
            await user.save()
            
            # Créer l'abonnement dans MongoDB
            await Subscription(
                user_id=user.id,
                plan=session["metadata"]["plan_id"],
                billing_cycle=session["metadata"]["billing_cycle"],
                stripe_subscription_id=session["subscription"],
                stripe_customer_id=session["customer"],
                status="active",
                current_period_start=datetime.now(),
                current_period_end=datetime.now() + timedelta(days=30)
            ).insert()
    
    return {"status": "success"}