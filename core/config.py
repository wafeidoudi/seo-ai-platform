from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # ==================== EMAIL ====================
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    
    # ==================== SMTP ====================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # ==================== APPLICATION ====================
    PROJECT_NAME: str = "SEO Platform PFE"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True
    
    # ==================== OPENROUTER AI ====================
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"
    
    # ==================== MONGODB ====================
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "seo_platform"
    
    # ==================== JWT / SECURITY ====================
    SECRET_KEY: str = "ton_secret_key_tres_long_et_securise_123456789"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ==================== BCRYPT ====================
    BCRYPT_ROUNDS: int = 12
    
    # ==================== STRIPE ====================
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_STARTER_MONTHLY: Optional[str] = None
    STRIPE_PRICE_STARTER_YEARLY: Optional[str] = None
    STRIPE_PRICE_PRO_MONTHLY: Optional[str] = None
    STRIPE_PRICE_PRO_YEARLY: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE_MONTHLY: Optional[str] = None
    STRIPE_PRICE_ENTERPRISE_YEARLY: Optional[str] = None
    
    # ==================== FRONTEND (UNE SEULE FOIS) ====================
    FRONTEND_URL: str = "http://localhost:5173"  # ← Garde celle-ci, supprime l'autre
    
    # ==================== RESEND (OPTIONNEL) ====================
    RESEND_API_KEY: Optional[str] = None  # ← CORRIGÉ : Optional avec None par défaut
    
    # ==================== CORS ====================
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()