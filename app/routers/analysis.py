from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.security import get_current_active_user
from app.models.user import User
from app.models.analysis import Analysis
from app.models.subscription import Subscription
from app.services.seo_crawler import crawl_website
from app.services.scoring import compute_scores
from app.services.gemini import generate_analysis_insights

router = APIRouter(tags=["Analysis"])


class LaunchAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)


class AnalysisResponse(BaseModel):
    message: str
    analysis_id: str
    global_score: int

    class Config:
        from_attributes = True


def serialize_analysis(analysis: Analysis, include_raw: bool = False) -> dict:
    data = {
        "id": str(analysis.id),
        "url": analysis.url,
        "global_score": analysis.global_score,
        "scores": {
            "global_score": analysis.global_score,
            "technical_seo": analysis.category_scores.get("technical", 0),
            "content_quality": analysis.category_scores.get("content", 0),
            "ux_ui": analysis.category_scores.get("ux", 0),
            "popularity": analysis.category_scores.get("popularity", 0),
        },
        "category_scores": analysis.category_scores,
        "score_explanations": analysis.score_explanations,
        "issues": analysis.issues,
        "recommendations": analysis.recommendations,
        "status": analysis.status,
        "created_at": analysis.created_at,
    }
    if include_raw:
        data["raw_data"] = analysis.raw_data
    return data


@router.post("/launch", response_model=AnalysisResponse)
async def launch_analysis(
    request: LaunchAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    url = request.url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    subscription = await Subscription.find_one(Subscription.user_id == str(current_user.id))
    if not subscription or not subscription.is_active():
        raise HTTPException(status_code=403, detail="No active subscription.")

    if not subscription.can_run_analysis():
        raise HTTPException(status_code=403, detail="Analysis quota exceeded. Upgrade your plan.")

    try:
        raw_data = await crawl_website(url)
        scores = compute_scores(raw_data)
        raw_issues = scores.get("issues", {})

        all_issues = []
        if isinstance(raw_issues, dict):
            for level in ["critical", "high", "medium", "low"]:
                all_issues.extend(raw_issues.get(level, []))
        else:
            all_issues = raw_issues

        ai_insights = await generate_analysis_insights(raw_data, scores, all_issues)

        analysis = Analysis(
            user_id=str(current_user.id),
            url=url,
            global_score=scores.get("global_score", 0),
            category_scores=scores.get("categories", {}),
            score_explanations=ai_insights.get("score_explanations", {}),
            raw_data=raw_data,
            issues=all_issues,
            recommendations=ai_insights.get("recommendations", []),
            status="completed",
        )
        await analysis.insert()

        subscription.analyses_used += 1
        await subscription.save()

        return {
            "message": "Analysis completed successfully",
            "analysis_id": str(analysis.id),
            "global_score": analysis.global_score,
        }
    except Exception as e:
        import logging

        logging.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/{id}")
async def get_analysis(
    id: str,
    current_user: User = Depends(get_current_active_user),
):
    analysis = await Analysis.get(id)
    if not analysis:
        raise HTTPException(404, "Analysis not found")

    if analysis.user_id != str(current_user.id) and not current_user.is_admin():
        raise HTTPException(403, "Access denied")

    return serialize_analysis(analysis, include_raw=True)


@router.get("/")
async def list_user_analyses(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
):
    analyses = await Analysis.find(Analysis.user_id == str(current_user.id)).sort(-Analysis.created_at).limit(limit).to_list()
    return {
        "total": len(analyses),
        "analyses": [serialize_analysis(analysis) for analysis in analyses],
    }
