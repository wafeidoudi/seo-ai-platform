# backend/debug_env.py
import sys
sys.path.insert(0, "backend")

from app.core.config import settings

print("🔍 Debug: Variables d'environnement chargées\n")
print(f"✅ OPENROUTER_API_KEY: {'[SET]' if settings.OPENROUTER_API_KEY else '[MISSING]'}")
print(f"✅ OPENROUTER_MODEL: {settings.OPENROUTER_MODEL}")
print(f"✅ OPENROUTER_BASE_URL: {settings.OPENROUTER_BASE_URL}")
print(f"✅ SECRET_KEY: {'[SET]' if settings.SECRET_KEY else '[MISSING]'}")
print(f"✅ MONGODB_URL: {settings.MONGODB_URL}")

# Afficher la clé (partiellement) pour vérification
if settings.OPENROUTER_API_KEY:
    key = settings.OPENROUTER_API_KEY
    print(f"\n🔑 Clé API (preview): {key[:15]}...{key[-4:]}")
    print(f"   Longueur: {len(key)} caractères")