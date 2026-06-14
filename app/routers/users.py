from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.db.mongodb import db
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import User
from app.core.security import (
    get_password_hash, verify_password, 
    get_current_active_user, get_current_admin_user
)

router = APIRouter(tags=["👤 Users"])

# ==================== SCHÉMAS ====================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# ==================== READ ====================

@router.get("/me", summary="Mon profil")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company": current_user.company,
        "role": current_user.role,
        "plan": current_user.plan,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

# ==================== UPDATE ====================

@router.put("/me", summary="Modifier mon profil")
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    update_data = user_update.dict(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(400, "No data to update")
    
    # Vérifier email unique
    if "email" in update_data and update_data["email"] != current_user.email:
        existing = await User.find_one(User.email == update_data["email"])
        if existing:
            raise HTTPException(400, "Email already exists")
    
    # Mettre à jour les champs
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.now()
    await current_user.save()
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "is_admin": current_user.role == "admin",
        "full_name": current_user.full_name,
        "company": current_user.company,
        "message": "Profile updated successfully"
    }

@router.post("/me/change-password", summary="Changer mot de passe")
async def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user)
):
    # Vérifier l'ancien mot de passe
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(400, "Current password is incorrect")
    
    # Vérifier que le nouveau est différent
    if password_data.current_password == password_data.new_password:
        raise HTTPException(400, "New password must be different")
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.now()
    await current_user.save()
    
    return {"message": "Password changed successfully"}

# ==================== ADMIN ROUTES ====================

@router.get("/", summary="Liste des utilisateurs (Admin)")
async def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user)  # ✅ CORRIGÉ
):
    users = await User.find_all().skip(skip).limit(limit).to_list()
    total = await User.count()
    
    return {
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "full_name": u.full_name,
                "company": u.company,
                "role": u.role,
                "plan": u.plan,
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None
            } for u in users
        ],
        "total": total,
        "page": (skip // limit) + 1,
        "limit": limit
    }

@router.get("/{user_id}", summary="Détails utilisateur (Admin)")
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)  # ✅ CORRIGÉ
):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "company": user.company,
        "role": user.role,
        "plan": user.plan,
        "is_active": user.is_active
    }

@router.delete("/{user_id}", summary="Supprimer utilisateur (Admin)")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user)  # ✅ CORRIGÉ
):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_active = False
    user.updated_at = datetime.now()
    await user.save()
    
    return {"message": "User deleted successfully"}