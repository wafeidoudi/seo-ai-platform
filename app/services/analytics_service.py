from app.models.export_log import ExportLog
from datetime import datetime, timedelta
from typing import Optional


class AnalyticsService:
    """Service for tracking and analyzing export usage"""

    @staticmethod
    async def track_export(user_id: int, **kwargs):
        log = ExportLog(user_id=user_id, **kwargs)
        await log.insert()
        return log

    @staticmethod
    async def get_export_stats(user_id: Optional[int] = None, days: int = 30) -> dict:
        since = datetime.utcnow() - timedelta(days=days)

        query = ExportLog.find(ExportLog.created_at >= since)

        if user_id:
            query = query.find(ExportLog.user_id == user_id)

        logs = await query.to_list()

        return {
            "total_exports": len(logs),
            "by_format": {
                fmt: len([l for l in logs if l.format == fmt])
                for fmt in ["pdf", "csv", "json"]
            },
            "by_section": {
                sec: len([l for l in logs if l.section == sec])
                for sec in set(l.section for l in logs)
            },
            "cache_hit_rate": round(
                sum(1 for l in logs if l.cache_hit) / max(1, len(logs)) * 100, 1
            ),
            "avg_generation_time_ms": round(
                sum(l.generation_time_ms or 0 for l in logs) /
                max(1, len(logs)), 0
            ),
            "period_days": days
        }