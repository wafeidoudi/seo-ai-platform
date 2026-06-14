# backend/app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.models.user import User
from fastapi import Depends, HTTPException, status
from app.models.user import User


# =============================
# PASSWORD HASHING CONFIG
# =============================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS
)

# =============================
# OAUTH2 SCHEME
# =============================
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


# =============================
# PASSWORD UTILITIES
# =============================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify if the plain password matches the hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


# =============================
# JWT TOKEN CREATION
# =============================
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""

    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# =============================
# GET CURRENT USER
# =============================
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """Retrieve the current user from JWT token"""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 🔎 Get user from database
    user = await User.get(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =============================
# ACTIVE USER CHECK
# =============================
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure the current user is active"""

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return current_user

# =============================
# ADMIN CHECK
# =============================
async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
):
    """Ensure the current user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ Accès réservé aux administrateurs"
        )
    return current_user