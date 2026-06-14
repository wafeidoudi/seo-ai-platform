
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime
import time, hashlib

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

# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(tags=["Export"])
cache_service = ReportCache()
# 🆕 ExportService créé dynamiquement selon la langue


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ExportRequest(BaseModel):
    """Request model for export endpoint"""
    url: str
    format: str = "pdf"
    section: str = "full"  # full, technical, content, ux, popularity, recommendations
    lang: str = "fr"  # 🆕 "fr" ou "en"
    include_reco: bool = True
    include_charts: bool = True
    use_cache: bool = True


class PreviewRequest(BaseModel):
    url: str
    section: str = "full"
    include_reco: bool = True


# ============================================================================
# RÉCUPÉRER DONNÉES DE LA BASE
# ============================================================================

async def fetch_analysis_from_db(url: str, user_id: str) -> Optional[Dict]:
    """
    Récupérer la dernière analyse depuis MongoDB avec TOUTES les données
    """
    try:
        from app.models.analysis import Analysis
        
        analysis = await Analysis.find_one(
            {"url": url, "user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if analysis:
            print(f"✅ Found analysis in DB for {url}")
            # Retourner TOUTES les données disponibles
            return {
                "technical": analysis.raw_data.get("technical", {}) if hasattr(analysis, 'raw_data') else {},
                "meta_tags": analysis.raw_data.get("meta_tags", {}) if hasattr(analysis, 'raw_data') else {},
                "headings": analysis.raw_data.get("headings", {}) if hasattr(analysis, 'raw_data') else {},
                "images": analysis.raw_data.get("images", []) if hasattr(analysis, 'raw_data') else [],
                "links": analysis.raw_data.get("links", {}) if hasattr(analysis, 'raw_data') else {},
                "raw_text": analysis.raw_data.get("raw_text", "") if hasattr(analysis, 'raw_data') else "",
                "scores": analysis.scores if hasattr(analysis, 'scores') else {},
                "category_scores": analysis.category_scores if hasattr(analysis, 'category_scores') else {},
                "issues": analysis.issues if hasattr(analysis, 'issues') else [],
                "recommendations": analysis.recommendations if hasattr(analysis, 'recommendations') else [],
                "score_explanations": analysis.score_explanations if hasattr(analysis, 'score_explanations') else {},
                "url": analysis.url if hasattr(analysis, 'url') else url,
                "created_at": analysis.created_at.isoformat() if hasattr(analysis, 'created_at') else datetime.utcnow().isoformat(),
            }
            
        print(f"⚠️ No analysis found in DB for {url}")
        return None
        
    except Exception as e:
        print(f"❌ Error fetching from DB: {e}")
        return None


# ============================================================================
# MAIN EXPORT ENDPOINT
# ============================================================================

@router.post("/")
async def export_report(
    request: ExportRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Generate and return an SEO analysis report.
    Récupère TOUTES les données de la base MongoDB.
    """
    
    url = request.url
    fmt = request.format
    section = request.section
    include_reco = request.include_reco
    include_charts = request.include_charts

    start_time = time.time()
    task_id = hashlib.md5(
        f"{current_user.id}{url}{datetime.utcnow()}".encode()
    ).hexdigest()[:10]

    # =====================================================================
    # ÉTAPE 1: RÉCUPÉRER LES DONNÉES RÉELLES DE LA BASE
    # =====================================================================
    
    db_data = await fetch_analysis_from_db(url, str(current_user.id))
    
    if not db_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Aucune analyse trouvée pour l'URL: {url}. Veuillez d'abord lancer une analyse."
        )
    
    raw_data = db_data
    
    # =====================================================================
    # ÉTAPE 2: CALCULER TOUS LES SCORES (ou utiliser ceux de la DB)
    # =====================================================================
    
    # Utiliser les scores de la DB si disponibles, sinon recalculer
    if db_data.get("scores"):
        scores = db_data["scores"]
        tech_score = scores.get("technical", 0)
        content_score = scores.get("content", 0)
        ux_score = scores.get("ux", 0)
        pop_score = scores.get("popularity", 0)
        global_score = scores.get("global_score", 0)
    else:
        tech_score, _ = score_technical(raw_data)
        content_score, _ = score_content(raw_data)
        ux_score, _ = score_ux(raw_data)
        pop_score, _ = score_popularity(raw_data)
        global_scores = compute_scores(raw_data)
        global_score = global_scores.get("global_score", 0)
        scores = {
            "technical": tech_score,
            "content": content_score,
            "ux": ux_score,
            "popularity": pop_score,
            "global": global_score
        }

    # =====================================================================
    # ÉTAPE 3: RÉCUPÉRER LES ISSUES DE LA DB
    # =====================================================================
    
    db_issues = db_data.get("issues", [])
    
    # Grouper les issues par catégorie
    tech_issues = [i for i in db_issues if i.get("category") == "technical"]
    content_issues = [i for i in db_issues if i.get("category") == "content"]
    ux_issues = [i for i in db_issues if i.get("category") == "ux"]
    pop_issues = [i for i in db_issues if i.get("category") == "popularity"]

    # =====================================================================
    # ÉTAPE 4: RÉCUPÉRER LES RECOMMENDATIONS DE LA DB
    # =====================================================================
    
    db_recommendations = db_data.get("recommendations", [])
    
    # Si c'est une liste (format backend), la convertir en dict par priorité
    if isinstance(db_recommendations, list):
        recommendations_by_priority = {"critical": [], "high": [], "medium": [], "low": []}
        for rec in db_recommendations:
            priority = rec.get("priority", "medium")
            if priority in recommendations_by_priority:
                recommendations_by_priority[priority].append(rec)
        db_recommendations = recommendations_by_priority

    # =====================================================================
    # ÉTAPE 5: CONSTRUIRE LA STRUCTURE COMPLÈTE AVEC TOUTES LES DONNÉES
    # =====================================================================
    data = {
        "technical": {
            "score": tech_score,
            "issues": tech_issues
        },
        "content": {
            "score": content_score,
            "issues": content_issues
        },
        "ux": {
            "score": ux_score,
            "issues": ux_issues
        },
        "popularity": {
            "score": pop_score,
            "issues": pop_issues
        },
        "scores": scores,
        "raw_data": raw_data,
        "recommendations": db_recommendations,
        "score_explanations": db_data.get("score_explanations", {})
    }

    # Métadonnées complètes
    data["meta"] = {
        "url": url,
        "url_analyzed": url,
        "user_id": current_user.id,
        "generated_at": datetime.utcnow().isoformat(),
        "section": section,
        "task_id": task_id,
        "analysis_date": db_data.get("created_at", datetime.utcnow().isoformat())
    }

    # =====================================================================
    # ÉTAPE 6: FILTRER PAR SECTION SI DEMANDÉ
    # =====================================================================
    if section != "full":
        filtered_data = {
            "meta": data["meta"],
            "scores": {
                "global": data["scores"].get("global", global_score),
                section: data["scores"].get(section, 0)
            },
            "raw_data": data.get("raw_data", {})
        }
        
        # Ajouter seulement la section demandée
        if section in data:
            filtered_data[section] = data[section]
        
        # Filtrer les recommendations par catégorie
        if include_reco and "recommendations" in data:
            all_recos = data["recommendations"]
            if isinstance(all_recos, dict):
                filtered_recos = {}
                for priority, recos in all_recos.items():
                    filtered_recos[priority] = [
                        r for r in recos 
                        if r.get("category") == section or section == "recommendations"
                    ]
                filtered_data["recommendations"] = filtered_recos
            elif isinstance(all_recos, list):
                filtered_data["recommendations"] = [
                    r for r in all_recos 
                    if r.get("category") == section or section == "recommendations"
                ]
        
        data = filtered_data

    # =====================================================================
    # ÉTAPE 7: GÉNÉRER L'EXPORT
    # =====================================================================
    
    if fmt == "json":
        return JSONResponse(content=data)

    # 🆕 Créer le service avec la langue demandée
    export_service = ExportService(lang=request.lang)

    if fmt == "pdf":
        file_path = await export_service.generate_pdf(
            data,
            include_charts=include_charts,
            user_id=str(current_user.id),
            task_id=task_id
        )
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"seo-report-{section}-{datetime.now().strftime('%Y-%m-%d')}.pdf"
        )

    if fmt == "csv":
        csv_buffer = export_service.generate_csv(data)
        return Response(
            content=csv_buffer.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": 
                f"attachment; filename=seo-report-{section}-{datetime.now().strftime('%Y-%m-%d')}.csv"
            }
        )

    raise HTTPException(status_code=400, detail=f"Format invalide: {fmt}. Utilisez: pdf, csv, json")


# ============================================================================
# AUTRES ENDPOINTS
# ============================================================================

@router.post("/preview")
async def preview_report(
    request: PreviewRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Prévisualisation du rapport (données brutes)"""
    db_data = await fetch_analysis_from_db(request.url, str(current_user.id))
    
    if not db_data:
        raise HTTPException(status_code=404, detail="Aucune analyse trouvée")
    
    return {
        "url": request.url,
        "section": request.section,
        "scores": db_data.get("scores", {}),
        "issues_count": len(db_data.get("issues", [])),
        "recommendations_count": len(db_data.get("recommendations", [])),
        "analysis_date": db_data.get("created_at")
    }


@router.get("/cache")
async def list_cached_reports(current_user: User = Depends(get_current_active_user)):
    return {"reports": cache_service.list_user_reports(str(current_user.id))}


@router.delete("/cache/{report_key}")
async def invalidate_cached_report(
    report_key: str,
    current_user: User = Depends(get_current_active_user)
):
    cache_service.invalidate_by_key(report_key)
    return {"message": "Rapport invalidé avec succès"}


print("✅ Export module PFE Pro loaded successfully")