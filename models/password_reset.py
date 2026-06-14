from beanie import Document, Indexed
from datetime import datetime, timedelta
from typing import Optional
from pydantic import EmailStr, Field
from bson import ObjectId

class PasswordResetToken(Document):
    """Token de réinitialisation de mot de passe"""
    email: (EmailStr)
    token: str = Field(..., unique=True)
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "password_reset_tokens"
        use_state_management = True
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        return not self.used and not self.is_expired