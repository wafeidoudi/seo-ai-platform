# backend/app/models/subscription.py
from beanie import Document, Indexed
from datetime import datetime
from typing import Optional, Literal
from pydantic import Field

class Subscription(Document):
    """Model to manage subscriptions and analysis quotas"""
    
    # 🔗 User reference
    user_id: Indexed(str)
    
    # 💳 Plan and billing
    plan: Literal["starter", "pro", "enterprise"]
    billing_cycle: Literal["monthly", "yearly"]
    price: float
    currency: str = "EUR"
    
    # 📊 Status and periods
    status: Literal["active", "canceled", "past_due"] = "active"
    current_period_start: datetime
    current_period_end: datetime
    
    # 📈 Analysis quotas
    analyses_limit: int = 10  # -1 = unlimited
    pages_per_analysis_limit: int = 10
    analyses_used: int = 0
    
    # 👤 Customer info (Stripe)
    customer_info: Optional[dict] = None
    
    # 🕐 Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    
    # ⚙️ Beanie configuration
    class Settings:
        name = "subscriptions"
        use_state_management = True
    
    # ✅ METHOD 1: Check if subscription is active
    def is_active(self) -> bool:
        """
        Check if the subscription is active and within its valid period
        
        Returns:
            bool: True if active and not expired, False otherwise
        """
        return self.status == "active" and datetime.now() < self.current_period_end
    
    # ✅ METHOD 2: Check if user can run an analysis (PREVIOUSLY MISSING!)
    def can_run_analysis(self) -> bool:
        """
        Check if the user is allowed to run a new analysis
        
        Returns:
            bool: True if quota available or unlimited, False otherwise
        """
        # Inactive subscription = no analyses allowed
        if not self.is_active():
            return False
        
        # -1 = unlimited analyses
        if self.analyses_limit == -1:
            return True
        
        # Check quota: used < limit
        return self.analyses_used < self.analyses_limit
    
    # ✅ METHOD 3: Increment analysis counter
    def increment_usage(self):
        """Increment the count of used analyses"""
        self.analyses_used += 1
        self.updated_at = datetime.now()
    
    # ✅ METHOD 4: Reset counter (for monthly reset or testing)
    def reset_usage(self):
        """Reset the analysis counter to 0"""
        self.analyses_used = 0
        self.updated_at = datetime.now()