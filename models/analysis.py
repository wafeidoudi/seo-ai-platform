# backend/app/models/analysis.py
from beanie import Document
from pydantic import Field, field_validator
from datetime import datetime

class Analysis(Document):
    """Modèle minimal - 100% compatible Pydantic v2"""
    
    user_id: str
    url: str
    global_score: int = 0
    category_scores: dict = Field(default_factory=dict)
    score_explanations: dict = Field(default_factory=dict)
    raw_data: dict = Field(default_factory=dict)
    issues: list = Field(default_factory=list)
    recommendations: list = Field(default_factory=list)
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("recommendations", mode="before")
    @classmethod
    def normalize_recommendations(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = value.get("recommendations")
            if isinstance(nested, list):
                return nested
            if isinstance(nested, dict):
                flattened = []
                for priority in ["critical", "high", "medium", "low"]:
                    for item in nested.get(priority, []):
                        if isinstance(item, dict):
                            flattened.append({**item, "priority": item.get("priority", priority)})
                return flattened
        return []

    class Settings:
        name = "analyses"
