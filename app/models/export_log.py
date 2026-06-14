from beanie import Document
from datetime import datetime
from typing import Optional


class ExportLog(Document):
    """Model for tracking export events (MongoDB - Beanie)"""
    
    user_id: str
    url_analyzed: str
    section: str
    lang: str = "fr"
    format: str
    
    
    cache_hit: bool = False
    file_size_kb: Optional[int] = None
    generation_time_ms: Optional[int] = None
    
    include_reco: bool = True
    include_charts: bool = True
    
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "export_logs"