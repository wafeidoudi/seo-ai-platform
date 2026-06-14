"""
SEO Platform - Export Router
Handles report generation endpoints for PDF, CSV, and JSON formats
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import os, time, hashlib, json

from app.core.security import get_current_active_user
from app.models.user import User
from app.services.export_service import ExportService
from app.services.scoring import (
    score_technical,
    score_content,
    score_ux,
    score_popularity,
    compute_scores
)
from app.services.recommendations import generate_recommendations
from app.services.cache_service import ReportCache
from app.services.analytics_service import AnalyticsService

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(tags=["Export"])

# Initialize singleton services
cache_service = ReportCache()
export_service = ExportService()
analytics_service = AnalyticsService()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ExportRequest(BaseModel):
    """Request model for export endpoint"""
    url: str
    format: str = "pdf"  # pdf, csv, json
    section: str = "full"  # full, technical, content, ux, popularity
    include_reco: bool = True
    include_charts: bool = True
    use_cache: bool = True


class PreviewRequest(BaseModel):
    """Request model for preview endpoint"""
    url: str
    section: str = "full"
    include_reco: bool = True


# ============================================================================
# MAIN EXPORT ENDPOINT
# ============================================================================

@router.post("/")
async def export_report(
    request: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    background_tasks: BackgroundTasks = None,
):
    """
    Generate and return an SEO analysis report.
    
    Supported formats: pdf, csv, json
    Supported sections: full, technical, content, ux, popularity
    """
    
    # Extract request parameters
    url = request.url
    fmt = request.format
    section = request.section
    include_reco = request.include_reco
    include_charts = request.include_charts
    use_cache = request.use_cache

    start_time = time.time()
    task_id = hashlib.md5(
        f"{current_user.id}{url}{datetime.utcnow()}".encode()
    ).hexdigest()[:10]

    # ========================================================================
    # FAKE RAW DATA (Replace with real crawler data in production)
    # ========================================================================
    raw_data = {
        "technical": {
            "has_robots_txt": True,
            "has_sitemap": True,
            "is_https": True,
            "has_viewport": True,
            "load_time_ms": 1800,
            "has_structured_data": False,
            "word_count": 800,
            "has_lang": True,
            "has_favicon": True,
            "html_size_kb": 120
        },
        "meta_tags": {
            "title": "Demo Page",
            "title_length": 45,
            "description": "SEO analysis demo",
            "description_length": 140
        },
        "headings": {
            "h1_count": 1,
            "h2_count": 3,
            "h3_count": 2
        },
        "images": [
            {"_summary": {"total": 5, "missing_alt": 1, "lazy_loaded": 3}}
        ],
        "links": {
            "internal": [{"url": "/"}, {"url": "/about"}],
            "external": [{"url": "https://google.com", "is_nofollow": False}]
        }
    }

    # ========================================================================
    # CALCULATE SCORES
    # ========================================================================
    tech_score, tech_issues = score_technical(raw_data)
    content_score, content_issues = score_content(raw_data)
    ux_score, ux_issues = score_ux(raw_data)
    pop_score, pop_issues = score_popularity(raw_data)
    global_scores = compute_scores(raw_data)

    # ========================================================================
    # BUILD DATA STRUCTURE FOR EXPORT
    # ========================================================================
    data = {
        "technical": {"score": tech_score, "issues": tech_issues},
        "content": {"score": content_score, "issues": content_issues},
        "ux": {"score": ux_score, "issues": ux_issues},
        "popularity": {"score": pop_score, "issues": pop_issues},
        "scores": {
            "technical": tech_score,
            "content": content_score,
            "ux": ux_score,
            "popularity": pop_score,
            "global": global_scores["global_score"]
        }
    }

    # Add recommendations if requested
    if include_reco:
        scores_for_reco = {
            "global_score": global_scores["global_score"],
            "categories": global_scores["categories"]
        }
        reco_result = generate_recommendations(raw_data, scores_for_reco)
        data["recommendations"] = reco_result["recommendations"]

    # Add metadata
    data["meta"] = {
        "url": url,
        "url_analyzed": url,
        "user_id": current_user.id,
        "generated_at": datetime.utcnow().isoformat(),
        "section": section
    }

    # ========================================================================
    # FILTER DATA BY SECTION (if not "full")
    # ========================================================================
    if section != "full":
        filtered_data = {
            "meta": data["meta"],
            "scores": data["scores"],
        }
        if section in data:
            filtered_data[section] = data[section]
        if include_reco and "recommendations" in data:
            filtered_data["recommendations"] = data["recommendations"]
        data = filtered_data

    # ========================================================================
    # GENERATE OUTPUT BY FORMAT
    # ========================================================================
    
    # JSON Export
    if fmt == "json":
        return JSONResponse(content=data)

    # PDF Export
    if fmt == "pdf":
        file_path = await export_service.generate_pdf(
            data,
            include_charts=include_charts,
            user_id=str(current_user.id),
            task_id=task_id
        )
        if background_tasks:
            background_tasks.add_task(export_service.cleanup_temp_file, file_path)
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"seo-report-{section}.pdf"
        )

    # CSV Export
    if fmt == "csv":
        csv_buffer = export_service.generate_csv(data)
        return Response(
            content=csv_buffer.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=seo-report-{section}.csv"}
        )

    # Invalid format
    raise HTTPException(
        status_code=400, 
        detail="Invalid format. Use: pdf, csv, or json"
    )


# ============================================================================
# PREVIEW ENDPOINT
# ============================================================================

@router.post("/preview")
async def preview_report(
    request: PreviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Generate a lightweight preview of the report"""
    return {
        "preview": "Preview generation not implemented yet",
        "section": request.section,
        "url": request.url
    }


# ============================================================================
# CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/cache")
async def list_cached_reports(
    current_user: User = Depends(get_current_active_user)
):
    """List cached reports for the authenticated user"""
    return {"reports": cache_service.list_user_reports(str(current_user.id))}


@router.delete("/cache/{report_key}")
async def invalidate_cached_report(
    report_key: str,
    current_user: User = Depends(get_current_active_user)
):
    """Invalidate a specific cached report"""
    cache_service.invalidate_by_key(report_key)
    return {"message": "Report invalidated successfully"}


print("✅ Export module loaded successfully")