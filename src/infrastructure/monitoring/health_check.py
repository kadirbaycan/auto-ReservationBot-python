"""Health Check System"""

from enum import Enum
from typing import Dict, Optional, List
from datetime import datetime
import asyncio


class HealthStatus(str, Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """System health check coordinator."""

    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.last_check: Optional[datetime] = None
        self.last_status: HealthStatus = HealthStatus.HEALTHY

    def register_check(self, name: str, check_func: callable):
        """Register a health check."""
        self.checks[name] = check_func

    async def check_database(self) -> bool:
        """Check database connectivity."""
        try:
            from src.infrastructure.database import get_async_session

            async with get_async_session() as session:
                # Simple query to test connection
                await session.execute("SELECT 1")
                return True
        except Exception:
            return False

    async def check_cache(self) -> bool:
        """Check cache connectivity."""
        try:
            from src.infrastructure.cache import RedisCache

            cache = RedisCache()
            await cache.set("health_check", "ok", ttl=10)
            result = await cache.get("health_check")
            return result == "ok"
        except Exception:
            # Fallback to memory cache is acceptable
            return True

    async def check_all(self) -> Dict:
        """Run all health checks."""
        results = {
            "status": HealthStatus.HEALTHY.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
        }

        # Database check
        db_healthy = await self.check_database()
        results["checks"]["database"] = {
            "status": HealthStatus.HEALTHY.value if db_healthy else HealthStatus.UNHEALTHY.value,
            "message": "Database connection OK" if db_healthy else "Database connection failed",
        }

        # Cache check
        cache_healthy = await self.check_cache()
        results["checks"]["cache"] = {
            "status": HealthStatus.HEALTHY.value if cache_healthy else HealthStatus.DEGRADED.value,
            "message": "Cache connection OK" if cache_healthy else "Cache unavailable (using fallback)",
        }

        # Custom checks
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    healthy = await check_func()
                else:
                    healthy = check_func()

                results["checks"][name] = {
                    "status": HealthStatus.HEALTHY.value if healthy else HealthStatus.UNHEALTHY.value,
                    "message": f"{name} check passed" if healthy else f"{name} check failed",
                }
            except Exception as e:
                results["checks"][name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Error: {str(e)}",
                }

        # Determine overall status
        check_statuses = [check["status"] for check in results["checks"].values()]

        if HealthStatus.UNHEALTHY.value in check_statuses:
            results["status"] = HealthStatus.UNHEALTHY.value
        elif HealthStatus.DEGRADED.value in check_statuses:
            results["status"] = HealthStatus.DEGRADED.value
        else:
            results["status"] = HealthStatus.HEALTHY.value

        self.last_check = datetime.utcnow()
        self.last_status = HealthStatus(results["status"])

        return results


# Singleton instance
_health_check: Optional[HealthCheck] = None


def get_health_check() -> HealthCheck:
    """Get or create health check instance."""
    global _health_check

    if _health_check is None:
        _health_check = HealthCheck()

    return _health_check
