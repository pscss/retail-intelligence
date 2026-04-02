"""Redis-backed rate limiting dependency for gateway."""

from datetime import UTC, datetime

from constants import CACHE_TTL_RATE_LIMIT
from fastapi import Header, HTTPException, status

from shared.redis_client import get_redis

REQUESTS_PER_MINUTE = 60


async def enforce_rate_limit(
    x_api_key: str | None = Header(default=None),
) -> None:
    """Apply per-key fixed-window rate limiting."""
    if not x_api_key:
        return

    minute_bucket = datetime.now(UTC).strftime("%Y%m%d%H%M")
    key = f"ratelimit:{x_api_key}:{minute_bucket}"

    redis = await get_redis()
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, CACHE_TTL_RATE_LIMIT)
    results = await pipe.execute()
    current = results[0]

    if current > REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again in one minute.",
        )
