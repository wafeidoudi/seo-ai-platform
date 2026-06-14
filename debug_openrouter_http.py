# backend/debug_openrouter_http.py
import asyncio
import httpx
import sys
sys.path.insert(0, "backend")

from app.core.config import settings

async def test_openrouter_http():
    print("🔌 Testing OpenRouter HTTP call...\n")
    
    api_key = settings.OPENROUTER_API_KEY
    base_url = settings.OPENROUTER_BASE_URL
    model = settings.OPENROUTER_MODEL
    
    print(f"📡 Endpoint: {base_url}/chat/completions")
    print(f"🤖 Model: {model}")
    print(f"🔑 Key preview: {api_key[:15]}...{api_key[-4:]}\n")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/pfeseo",
        "X-Title": "PFESEO Debug"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello, respond with just 'OK'"}],
        "max_tokens": 10
    }
    
    try:
        print("⏳ Sending request...")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            print(f"\n📊 Response Status: {response.status_code}")
            print(f"📦 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS!")
                print(f"🤖 Response: {data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
                print(f"📊 Model used: {data.get('model')}")
                return True
            else:
                print(f"\n❌ ERROR {response.status_code}")
                print(f"💬 Response body: {response.text}")
                
                # Interpréter les erreurs courantes
                if response.status_code == 401:
                    print("\n🔑 401 = Clé API invalide ou expirée")
                    print("   → Va sur https://openrouter.ai/keys et régénère ta clé")
                elif response.status_code == 403:
                    print("\n🚫 403 = Clé valide mais sans crédits ou modèle indisponible")
                    print("   → Vérifie ton dashboard OpenRouter pour les crédits")
                elif response.status_code == 404:
                    print("\n❓ 404 = Modèle ou endpoint introuvable")
                    print("   → Vérifie que le modèle '{model}' existe sur OpenRouter")
                elif response.status_code == 429:
                    print("\n⏱️ 429 = Rate limit dépassé")
                    print("   → Attends 1 minute ou utilise un autre modèle")
                elif response.status_code >= 500:
                    print("\n🔧 5xx = Problème côté OpenRouter")
                    print("   → Réessaie dans quelques minutes")
                
                return False
                
    except httpx.ConnectError as e:
        print(f"\n🌐 Connection Error: {e}")
        print("   → Vérifie ta connexion internet")
        print("   → Essaye d'accéder à https://openrouter.ai dans ton navigateur")
        return False
    except httpx.TimeoutException as e:
        print(f"\n⏰ Timeout Error: {e}")
        print("   → L'API met trop de temps à répondre")
        print("   → Essaye avec un modèle plus léger comme 'openai/gpt-3.5-turbo'")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_openrouter_http())
    sys.exit(0 if result else 1)