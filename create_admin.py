import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.core.database import init_db
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime

async def create_admin():
    await init_db()
    
    # ✅ Maintenant User.email fonctionne avec Indexed
    existing = await User.find_one(User.email == "admin@pfeseo.com")
    if existing:
        print("❌ Admin existe déjà !")
        print(f"   ID: {existing.id}")
        print(f"   Role: {existing.role}")
        return
    
    # Crée l'admin
    admin = User(
        email="admin@pfeseo.com",
        password_hash=get_password_hash("admin123"),
        full_name="PFESEO Admin",
        company="PFESEO",
        goal="seo",
        plan="enterprise",
        role="admin",
        is_active=True,
        created_at=datetime.now(),
        last_login=None,
        updated_at=None
    )
    
    await admin.insert()
    print("✅ Admin créé avec succès !")
    print(f"   Email: admin@pfeseo.com")
    print(f"   Password: admin123")
    print(f"   Role: admin")
    print(f"   ID: {admin.id}")

if __name__ == "__main__":
    asyncio.run(create_admin())