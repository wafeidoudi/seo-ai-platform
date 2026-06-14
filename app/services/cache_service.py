import redis, json, hashlib, os
from datetime import datetime, timedelta
from typing import Optional, List, Dict


class ReportCache:
    """Redis-based caching service for SEO reports"""
    
    def _init_(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.TTL_HOURS = 24
        self.PREFIX = "report"
    
    def _generate_key(self, url: str, section: str, format: str, user_id: str) -> str:
        """Generate a unique cache key"""
        raw = f"{user_id}:{url}:{section}:{format}"
        hash_key = hashlib.md5(raw.encode()).hexdigest()[:16]
        return f"{self.PREFIX}:{user_id}:{hash_key}"
    
    def get(self, url: str, section: str, format: str, user_id: str) -> Optional[Dict]:
        """Retrieve a report from cache"""
        key = self._generate_key(url, section, format, user_id)
        cached = self.redis.get(key)
        if cached:
            data = json.loads(cached)
            # Refresh TTL on access
            self.redis.expire(key, timedelta(hours=self.TTL_HOURS))
            return data
        return None
    
    def set(self, url: str, section: str, format: str, user_id: str, 
            file_path: str, metadata: Dict) -> str:
        """Store a report in cache"""
        key = self._generate_key(url, section, format, user_id)
        data = {
            "file_path": file_path,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=self.TTL_HOURS)).isoformat()
        }
        self.redis.setex(key, timedelta(hours=self.TTL_HOURS), json.dumps(data))
        return key
    
    def invalidate(self, url: str, section: str, format: str, user_id: str):
        """Invalidate a specific report"""
        key = self._generate_key(url, section, format, user_id)
        self.redis.delete(key)
    
    def invalidate_by_key(self, key: str):
        """Invalidate by direct key"""
        full_key = f"{self.PREFIX}:{key}" if not key.startswith(self.PREFIX) else key
        self.redis.delete(full_key)
    
    def list_user_reports(self, user_id: str) -> List[Dict]:
        """List all cached reports for a user"""
        reports = []
        pattern = f"{self.PREFIX}:{user_id}:*"
        for key in self.redis.scan_iter(match=pattern):
            cached = self.redis.get(key)
            if cached:
                data = json.loads(cached)
                reports.append({
                    "key": key,
                    "metadata": data.get("metadata", {}),
                    "created_at": data.get("created_at"),
                    "expires_at": data.get("expires_at"),
                    "file_exists": os.path.exists(data.get("file_path", ""))
                })
        return reports
    
    def cleanup_expired(self):
        """Clean up expired physical files (run via cron job)"""
        # Optional implementation for disk cleanup
        pass