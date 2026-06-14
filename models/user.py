# backend/app/models/user.py
from beanie import Document, Indexed, PydanticObjectId
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from beanie import Document
from typing import Optional

class User(Document):
    """Modèle utilisateur pour MongoDB"""
    id: PydanticObjectId = Field(default_factory=PydanticObjectId, alias="_id")
    email: Indexed(EmailStr, unique=True)  # ← CORRIGÉ : Indexed(EmailStr, unique=True)
    password_hash: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company: Optional[str] = None
    goal: str = "seo"  # seo/performance/other
    plan: str = "starter"  # starter/pro/enterprise
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    is_active: bool = True
    updated_at: Optional[datetime] = None
    role: str = "user"   # user/admin
    class Settings:
        name = "users"
        use_state_management = True
    
    def __repr__(self):
        return f"<User {self.email}>"
    
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"