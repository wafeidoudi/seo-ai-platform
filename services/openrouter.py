# backend/app/services/openrouter.py
import httpx
from typing import Optional, List, Dict, Any
from app.core.config import settings

class OpenRouterClient:
    """Client async pour l'API OpenRouter (compatible OpenAI)"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.default_model = settings.OPENROUTER_MODEL
        self.timeout = 60.0  # secondes
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Envoyer une requête de chat completion à OpenRouter
        
        Args:
            messages: Liste de messages [{"role": "user", "content": "..."}]
            model: Nom du modèle (ex: "google/gemini-2.0-flash-exp:free")
            system_prompt: Prompt système optionnel
            temperature: Créativité (0.0 à 1.0)
            max_tokens: Limite de tokens en réponse
            
        Returns:
            Dict avec la réponse de l'assistant
        """
        # Préparer les messages avec system prompt si fourni
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        # Headers requis par OpenRouter
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ton-user/pfeseo",  # Optionnel mais recommandé
            "X-Title": "PFESEO Platform"  # Optionnel
        }
        
        # Payload de la requête
        payload = {
            "model": model or self.default_model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                # Extraire la réponse de l'assistant
                assistant_message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                return {
                    "success": True,
                    "response": assistant_message,
                    "model_used": data.get("model"),
                    "usage": data.get("usage", {}),
                    "raw_data": data  # Pour debugging si besoin
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP Error {e.response.status_code}: {e.response.text}",
                "response": None
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request Error: {str(e)}",
                "response": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected Error: {str(e)}",
                "response": None
            }
    
    async def test_connection(self) -> bool:
        """Tester la connexion à l'API OpenRouter"""
        result = await self.chat_completion(
            messages=[{"role": "user", "content": "Hello, are you there? Respond with just 'OK'."}],
            max_tokens=10
        )
        return result["success"] and "ok" in result["response"].lower()


# Instance globale pour réutilisation
openrouter_client = OpenRouterClient()