# backend/list_openrouter_models.py
import asyncio
import httpx
import sys
sys.path.insert(0, "backend")

from app.core.config import settings

async def list_free_models():
    print("🔍 Fetching available FREE models from OpenRouter...\n")
    
    api_key = settings.OPENROUTER_API_KEY
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Endpoint pour lister les modèles
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.text}")
                return
            
            data = response.json()
            models = data.get("data", [])
            
            # Filtrer les modèles gratuits
            free_models = [
                m for m in models 
                if m.get("pricing", {}).get("prompt") == "0" 
                or ":free" in m.get("id", "")
            ]
            
            print(f"✅ Found {len(free_models)} free models:\n")
            print("💡 Copie l'ID d'un modèle ci-dessous dans ton .env\n")
            print("─" * 70)
            
            for i, model in enumerate(free_models[:15], 1):  # Top 15
                model_id = model.get("id", "unknown")
                name = model.get("name", "Unknown")
                print(f"{i}. {model_id}")
                print(f"   📛 {name}")
                print()
            
            print("─" * 70)
            print("\n📝 Exemple pour .env :")
            if free_models:
                print(f"OPENROUTER_MODEL={free_models[0].get('id')}")
                
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print("\n🔄 Alternative: Va sur https://openrouter.ai/models dans ton navigateur")

if __name__ == "__main__":
    asyncio.run(list_free_models())