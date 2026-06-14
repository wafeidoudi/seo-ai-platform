# backend/test_openrouter.py
import asyncio
import sys
sys.path.insert(0, "backend")

from app.services.openrouter import openrouter_client

async def test():
    print("🔌 Testing OpenRouter connection...")
    
    # Test 1: Connection check
    is_connected = await openrouter_client.test_connection()
    print(f"✅ Connection: {'OK' if is_connected else 'FAILED'}")
    
    if not is_connected:
        print("❌ Check your OPENROUTER_API_KEY in .env")
        return
    
    # Test 2: Simple chat
    print("\n💬 Testing chat completion...")
    result = await openrouter_client.chat_completion(
        messages=[{"role": "user", "content": "What is SEO in one sentence?"}],
        system_prompt="You are a helpful SEO expert assistant.",
        max_tokens=100
    )
    
    if result["success"]:
        print(f"✅ Response: {result['response']}")
        print(f"📊 Model: {result['model_used']}")
    else:
        print(f"❌ Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(test())