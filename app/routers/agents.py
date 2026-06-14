from typing import Optional, Dict, Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.security import get_current_active_user
from app.models.user import User
from app.services.gemini import ai_client
from app.services.agent_prompts import get_agent_prompt

router = APIRouter(tags=["AI Agents"])

AgentType = Literal["technical", "content", "ux", "popularity", "recommendation"]


class AgentChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


@router.post("/{agent_type}/chat")
async def agent_chat(
    agent_type: AgentType,
    request: AgentChatRequest,
    current_user: User = Depends(get_current_active_user),
):
    system_prompt = await get_agent_prompt(agent_type)
    if not system_prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Agent type '{agent_type}' not supported")

    context = request.context or {}
    enriched_context = ""
    if context.get("analysis"):
        analysis = context["analysis"]
        enriched_context = (
            f"\nLatest SEO analysis:\n"
            f"URL: {analysis.get('url', 'N/A')}\n"
            f"Scores: {analysis.get('scores') or analysis.get('category_scores')}\n"
            f"Explanations: {analysis.get('score_explanations', {})}\n"
            f"Issues: {analysis.get('issues', [])[:8]}\n"
            f"Recommendations: {analysis.get('recommendations', [])[:5]}\n"
        )

    result = await ai_client.generate_text(
        prompt=f"{request.message}\n\nContext:{enriched_context}",
        system_prompt=system_prompt,
        temperature=0.5,
        max_tokens=1800,
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Gemini service error: {result['error']}")

    return {
        "agent_type": agent_type,
        "response": result["response"],
        "model_used": result["model_used"],
        "usage": result.get("usage", {}),
    }


@router.get("/types")
async def get_agent_types():
    return {
        "agents": [
            {
                "type": "technical",
                "name": "Technical SEO Agent",
                "description": "Expert in performance, crawlability, Core Web Vitals, and indexability",
                "icon": "fa-wrench",
            },
            {
                "type": "content",
                "name": "Content Agent",
                "description": "Expert in metadata, heading structure, content depth, and keyword clarity",
                "icon": "fa-file-lines",
            },
            {
                "type": "ux",
                "name": "UX/UI Agent",
                "description": "Expert in accessibility, mobile usability, and experience signals",
                "icon": "fa-paintbrush",
            },
            {
                "type": "popularity",
                "name": "Popularity Agent",
                "description": "Expert in internal links, authority signals, and off-page strategy",
                "icon": "fa-star",
            },
            {
                "type": "recommendation",
                "name": "Recommendation Agent",
                "description": "Synthesizes all results into prioritized actions",
                "icon": "fa-lightbulb",
            },
        ]
    }
