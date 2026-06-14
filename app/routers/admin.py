from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.analysis import Analysis
from app.services.agent_prompts import list_prompts, update_prompt
from app.routers.analysis import serialize_analysis

router = APIRouter(tags=["Admin"])


class PromptUpdate(BaseModel):
    title: str | None = None
    content: str = Field(..., min_length=20)


@router.get("/activity")
async def get_activity(current_user: User = Depends(get_current_admin_user)):
    # Plus besoin de require_admin, get_current_admin_user fait le travail
    users = await User.find_all().sort(-User.created_at).to_list()
    reports = await Analysis.find_all().sort(-Analysis.created_at).limit(100).to_list()

    return {
        "users": [
            {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "company": user.company,
                "plan": user.plan,
                "goal": user.goal,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": user.last_login,
            }
            for user in users
        ],
        "reports": [serialize_analysis(report) | {"user_id": report.user_id} for report in reports],
    }


@router.get("/reports")
async def get_reports(current_user: User = Depends(get_current_admin_user)):
    reports = await Analysis.find_all().sort(-Analysis.created_at).limit(200).to_list()
    return {"total": len(reports), "reports": [serialize_analysis(report) | {"user_id": report.user_id} for report in reports]}


@router.get("/prompts")
async def get_prompts(current_user: User = Depends(get_current_admin_user)):
    return {"prompts": await list_prompts()}


@router.put("/prompts/{key}")
async def put_prompt(
    key: str,
    prompt: PromptUpdate,
    current_user: User = Depends(get_current_admin_user),
):
    return await update_prompt(
        key=key,
        content=prompt.content,
        title=prompt.title,
        updated_by=str(current_user.id),
    )