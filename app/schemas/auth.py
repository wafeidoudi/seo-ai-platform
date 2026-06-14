from pydantic import BaseModel, EmailStr, Field
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field, field_serializer, ConfigDict
from datetime import datetime
from typing import Optional, List

# ==================== INSCRIPTION ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 caractères")
    full_name: Optional[str] = None
    company: Optional[str] = None
    goal: Optional[str] = "seo"

# ==================== CONNEXION ====================
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ==================== TOKEN ====================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==================== RÉPONSE UTILISATEUR (PYDANTIC V2) ====================
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    company: Optional[str]
    goal: str
    plan: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

    # ✅ Pydantic v2 config
    model_config = ConfigDict(from_attributes=True)
    
    # ✅ Serializer pour ObjectId → str
    @field_serializer('id')
    def serialize_id(self, value):
        return str(value) if value else None

# ==================== MISE À JOUR PROFIL ====================
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    goal: Optional[str] = None

# ==================== CHANGEMENT MOT DE PASSE ====================
class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

# ==================== LISTE UTILISATEURS ====================
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int = 1
    limit: int = 100

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class PasswordResetResponse(BaseModel):
    message: str
    success: bool