import json
import asyncio
import random
from typing import Any

import httpx

from app.core.config import settings
from app.services.agent_prompts import get_agent_prompt


# ==================== GEMINI CLIENT ====================

class GeminiClient:
    MAX_RETRIES = 1  # Minimal retries — free tier quota is 0
    BASE_DELAY = 1.0
    MAX_DELAY = 10.0
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = settings.GEMINI_BASE_URL.rstrip("/")
        self.timeout = 60.0

    def _extract_retry_after(self, response: httpx.Response) -> float:
        retry_after = response.headers.get("retry-after")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        try:
            error_data = response.json()
            details = error_data.get("error", {}).get("details", [])
            for detail in details:
                if detail.get("@type", "").endswith("RetryInfo"):
                    delay_str = detail.get("retryDelay", "0s")
                    if delay_str.endswith("s"):
                        return float(delay_str[:-1])
        except Exception:
            pass
        return self.BASE_DELAY

    def _calculate_backoff(self, attempt: int, retry_after: float | None = None) -> float:
        if retry_after and retry_after > 0:
            base = retry_after
        else:
            base = self.BASE_DELAY * (2 ** attempt)
        jitter = base * 0.25
        delay = base + random.uniform(-jitter, jitter)
        return min(delay, self.MAX_DELAY)

    async def _make_request(self, client: httpx.AsyncClient, payload: dict[str, Any]) -> httpx.Response:
        for attempt in range(self.MAX_RETRIES):
            response = await client.post(
                f"{self.base_url}/models/{self.model}:generateContent",
                params={"key": self.api_key},
                json=payload,
            )
            if response.status_code == 200:
                return response
            if response.status_code not in self.RETRYABLE_STATUS_CODES:
                response.raise_for_status()
            retry_after = self._extract_retry_after(response)
            delay = self._calculate_backoff(attempt, retry_after)
            if attempt < self.MAX_RETRIES - 1:
                await asyncio.sleep(delay)
                continue
            response.raise_for_status()
        raise httpx.HTTPStatusError(
            "Max retries exceeded", request=None, response=httpx.Response(429, text="Rate limit")
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "Gemini API key not configured", "response": None}
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(client, payload)
                data = response.json()
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return {
                    "success": True,
                    "response": text,
                    "model_used": self.model,
                    "usage": data.get("usageMetadata", {}),
                    "raw_data": data,
                }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"Gemini HTTP {e.response.status_code}: {e.response.text}",
                "response": None,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "response": None}

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 3000,
    ) -> dict[str, Any]:
        result = await self.generate_text(
            prompt=prompt, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens
        )
        if not result["success"]:
            return result
        text = result["response"].strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            result["json"] = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            result["success"] = False
            result["error"] = f"Gemini returned invalid JSON: {e}"
            return result


ai_client = GeminiClient()


# ==================== OPENROUTER CLIENT ====================

class OpenRouterClient:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.timeout = 60.0

    def _build_messages(self, prompt: str, system_prompt: str | None = None) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        if not self.api_key:
            return {"success": False, "error": "OpenRouter API key not configured", "response": None}
        payload = {
            "model": self.model,
            "messages": self._build_messages(prompt, system_prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.FRONTEND_URL,
            "X-Title": settings.PROJECT_NAME,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {
                    "success": True,
                    "response": text,
                    "model_used": self.model,
                    "usage": data.get("usage", {}),
                    "raw_data": data,
                    "provider": "openrouter",
                }
        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"OpenRouter HTTP {e.response.status_code}: {e.response.text}",
                "response": None,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "response": None}

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 3000,
    ) -> dict[str, Any]:
        json_instruction = "You must respond with valid JSON only. No markdown, no explanations outside the JSON."
        combined_system = f"{system_prompt}\n\n{json_instruction}" if system_prompt else json_instruction
        result = await self.generate_text(
            prompt=prompt, system_prompt=combined_system, temperature=temperature, max_tokens=max_tokens
        )
        if not result["success"]:
            return result
        text = result["response"].strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            result["json"] = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            result["success"] = False
            result["error"] = f"OpenRouter returned invalid JSON: {e}"
            return result


openrouter_client = OpenRouterClient()


# ==================== UNIFIED AI CLIENT ====================

class AIClient:
    """Unified client: tries Gemini, falls back to OpenRouter on quota errors."""

    def __init__(self):
        self.primary = ai_client
        self.fallback = openrouter_client

    def _is_quota_error(self, result: dict[str, Any]) -> bool:
        if result.get("success"):
            return False
        error_str = str(result.get("error", "")).lower()
        return any(k in error_str for k in ["429", "quota", "rate limit", "resource_exhausted"])

    async def generate_json(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 3000,
    ) -> dict[str, Any]:
        # Try Gemini first (if key exists)
        if settings.GEMINI_API_KEY:
            result = await self.primary.generate_json(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if result.get("success"):
                result["provider"] = "gemini"
                return result
            if not self._is_quota_error(result):
                return result  # Non-quota error, don't fallback
            # Quota error — fall through to OpenRouter
            primary_error = result.get("error")
        else:
            primary_error = "Gemini API key not set"

        # Fallback to OpenRouter
        print(f"[AIClient] Gemini failed, falling back to OpenRouter... ({str(primary_error)[:100]})")
        fallback = await self.fallback.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if fallback.get("success"):
            fallback["provider"] = "openrouter"
            fallback["fallback_used"] = True
            fallback["primary_error"] = primary_error
        return fallback

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        if settings.GEMINI_API_KEY:
            result = await self.primary.generate_text(
                prompt=prompt, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens
            )
            if result.get("success"):
                result["provider"] = "gemini"
                return result
            if not self._is_quota_error(result):
                return result
            primary_error = result.get("error")
        else:
            primary_error = "Gemini API key not set"

        fallback = await self.fallback.generate_text(
            prompt=prompt, system_prompt=system_prompt, temperature=temperature, max_tokens=max_tokens
        )
        if fallback.get("success"):
            fallback["provider"] = "openrouter"
            fallback["fallback_used"] = True
            fallback["primary_error"] = primary_error
        return fallback


# EXPORT THIS — use it everywhere
ai_client = AIClient()


# ==================== FALLBACK INSIGHTS ====================

def _fallback_insights(scores: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, Any]:
    categories = scores.get("categories", {})
    grouped = {key: [] for key in ["technical", "content", "ux", "popularity"]}
    for issue in issues:
        category = issue.get("category") or "technical"
        grouped.setdefault(category, []).append(issue)

    def score_label(score: int) -> str:
        if score >= 80:
            return "strong"
        if score >= 60:
            return "moderate"
        if score >= 40:
            return "weak"
        return "poor"

    def issue_titles(key: str, limit: int = 2) -> str:
        related = grouped.get(key, [])
        titles = [item.get("title") for item in related[:limit] if item.get("title")]
        if not titles:
            return "no major blocking issues"
        if len(titles) == 1:
            return titles[0]
        return f"{titles[0]} and {titles[1]}"

    def explain(key: str, label: str) -> str:
        score = categories.get(key, 0)
        related = grouped.get(key, [])
        level = score_label(score)
        if key == "technical":
            if related:
                return f"{label} is {score}/100 ({level}) because core checks passed, but {issue_titles(key)} reduce crawlability and rich-result readiness."
            return f"{label} is {score}/100 ({level}) because HTTPS, crawl, mobile, performance, and structured-data checks mostly passed."
        if key == "content":
            if related:
                return f"{label} is {score}/100 ({level}) because search snippets and page structure need work, especially {issue_titles(key)}."
            return f"{label} is {score}/100 ({level}) because title, description, headings, and depth checks are mostly healthy."
        if key == "ux":
            if related:
                return f"{label} is {score}/100 ({level}); most UX checks passed, but accessibility or interface signals still need fixes such as {issue_titles(key)}."
            return f"{label} is {score}/100 ({level}) because mobile, image accessibility, language, and branding checks mostly passed."
        if key == "popularity":
            if related:
                return f"{label} is {score}/100 ({level}) based on visible link signals; {issue_titles(key)} show that off-page authority still needs validation."
            return f"{label} is {score}/100 ({level}) based on internal and external link signals visible in the crawl."
        if related:
            return f"{label} is {score}/100 ({level}) because {issue_titles(key)} limits the result."
        return f"{label} is {score}/100 ({level}) based on the measured SEO signals."

    recommendations = []
    for index, issue in enumerate(issues[:8]):
        priority = issue.get("priority", "medium")
        if priority == "critical":
            priority = "high"
        category = issue.get("category", "technical")
        title = issue.get("title", "Improve SEO issue")
        solution = issue.get("solution", "Review and fix this issue.")
        recommendations.append({
            "id": issue.get("id", f"issue-{index}"),
            "priority": priority,
            "category": category,
            "title": title,
            "description": f"{issue.get('description', 'This issue was detected during the crawl')} This contributes to the {categories.get(category, 0)}/100 {category} score.",
            "impact": issue.get("impact", "Improves SEO quality and search visibility."),
            "effort": "Medium" if category in {"technical", "popularity"} else "Low",
            "actions": [
                solution,
                f"Re-run the analysis and confirm the {category} score improves.",
            ],
            "agent": category,
        })

    return {
        "score_explanations": {
            "global": (
                f"Global SEO score is {scores.get('global_score', 0)}/100 because Technical SEO contributes "
                f"{categories.get('technical', 0)}/100, Content Quality {categories.get('content', 0)}/100, "
                f"UX/UI {categories.get('ux', 0)}/100, and Popularity {categories.get('popularity', 0)}/100."
            ),
            "technical": explain("technical", "Technical SEO"),
            "content": explain("content", "Content Quality"),
            "ux": explain("ux", "UX/UI"),
            "popularity": explain("popularity", "Popularity"),
        },
        "recommendations": recommendations,
    }


# ==================== THE ONLY FUNCTION THAT MATTERS ====================

async def generate_analysis_insights(
    raw_data: dict[str, Any],
    scores: dict[str, Any],
    issues: list[dict[str, Any]]
) -> dict[str, Any]:
    system_prompt = await get_agent_prompt("recommendation")
    compact_data = {
        "url": raw_data.get("url"),
        "scores": scores,
        "issues": issues[:20],
        "meta_tags": raw_data.get("meta_tags", {}),
        "headings": raw_data.get("headings", {}),
        "technical": raw_data.get("technical", {}),
        "performance": raw_data.get("performance", {}),
        "images_summary": next((item.get("_summary") for item in raw_data.get("images", []) if item.get("_summary")), {}),
        "links_count": {
            "internal": len(raw_data.get("links", {}).get("internal", [])),
            "external": len(raw_data.get("links", {}).get("external", [])),
        },
    }

    # CRITICAL: Use ai_client, NOT ai_client
    result = await ai_client.generate_json(
        prompt=json.dumps(compact_data, ensure_ascii=False, default=str),
        system_prompt=system_prompt,
        temperature=0.2,
        max_tokens=3000,
    )

    if result.get("success") and isinstance(result.get("json"), dict):
        data = result["json"]
        if "score_explanations" in data and "recommendations" in data:
            data["provider"] = result.get("provider", "unknown")
            if result.get("fallback_used"):
                data["fallback_used"] = True
                data["primary_error"] = result.get("primary_error")
            return data

    return _fallback_insights(scores, issues)