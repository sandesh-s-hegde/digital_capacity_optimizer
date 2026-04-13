import json
import os
import logging
from redis.asyncio import Redis, ConnectionPool

logger = logging.getLogger("digital-twin")

class PredictionCache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.pool = ConnectionPool.from_url(redis_url, decode_responses=True)
        self.client = Redis(connection_pool=self.pool)
        self.ttl_seconds = 600  # 10 minute semantic cache

    async def get_prediction(self, cache_key: str) -> dict | None:
        """Retrieves a cached AI prediction to bypass expensive LLM/Monte Carlo compute."""
        try:
            cached_data = await self.client.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for key: {cache_key}. Bypassing AI inference.")
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.warning(f"Redis cache read failed, falling back to compute: {str(e)}")
            return None

    async def set_prediction(self, cache_key: str, prediction_data: dict) -> None:
        """Stores a successful AI prediction with a 10-minute TTL."""
        try:
            await self.client.setex(
                name=cache_key,
                time=self.ttl_seconds,
                value=json.dumps(prediction_data)
            )
        except Exception as e:
            logger.warning(f"Redis cache write failed: {str(e)}")

prediction_cache = PredictionCache()
