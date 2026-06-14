import secrets
import string
import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.auth import (
    ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse,
    UserRegister, UserLogin, Token, UserResponse
)
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_active_user
from app.core.email import send_reset_email
from app.core.config import settings
import asyncio
# ✅ UN SEUL router
router = APIRouter(tags=["🔐 Authentication"])

# ================= REGISTER =================
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserRegister):
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(400, "Email already exists")

    user = User(
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        company=user_in.company,
        goal=user_in.goal or "seo"
    )
    await user.insert()

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        goal=user.goal,
        plan=user.plan,
        created_at=user.created_at,
        last_login=user.last_login,
        is_active=user.is_active
    )

# ================= CURRENT USER =================
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        company=current_user.company,
        goal=current_user.goal,
        plan=current_user.plan,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        is_active=current_user.is_active
    )

# ================= LOGIN =================
@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    user = await User.find_one(User.email == user_in.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.last_login = datetime.now()
    await user.save()

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": user.is_admin  # ← AJOUTÉ : retourne is_admin
    }

def generate_reset_token() -> str:
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))

# ==================== FORGOT PASSWORD ====================
def generate_temp_password(length=10):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):

    user = await User.find_one(User.email == request.email)

    if user:

        # generate new temporary password
        temp_password = generate_temp_password()

        user.password_hash = get_password_hash(temp_password)
        await user.save()

        await asyncio.to_thread(
            send_reset_email,
            request.email,
            temp_password,
            user.full_name or "",
            True
        )

    return {
        "message": "If this email exists, a new password has been sent.",
        "success": True
    }

# ==================== VERIFY TOKEN ====================
@router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    reset_token = await PasswordResetToken.find_one(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False
    )
    
    if not reset_token or reset_token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    return {"valid": True, "email": reset_token.email}

# ==================== RESET PASSWORD ====================
@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: ResetPasswordRequest):
    reset_token = await PasswordResetToken.find_one(
        PasswordResetToken.token == request.token,
        PasswordResetToken.used == False
    )
    
    if not reset_token or reset_token.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = await User.find_one(User.email == reset_token.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password_hash = get_password_hash(request.new_password)
    user.updated_at = datetime.now()
    await user.save()
    
    reset_token.used = True
    await reset_token.save()
    
    await PasswordResetToken.find(
        PasswordResetToken.email == reset_token.email,
        PasswordResetToken.used == False
    ).update({"$set": {"used": True}})
    
    return PasswordResetResponse(
        message="Password reset successfully. You can now log in.",
        success=True
    )