"""Sentiment analysis service."""

import hashlib
import time

from constants import CACHE_TTL_INFERENCE

from inference_service.model_loader import model_loader
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import SentimentResponse
from shared.redis_client import get_redis


class SentimentService:
    """Handles sentiment analysis inference."""

    async def analyze(self, request: InferenceRequest) -> SentimentResponse:
        """Run sentiment analysis, check cache first."""
        input_hash = hashlib.sha256(request.text.encode()).hexdigest()
        cache_key = f"inference:sentiment:{input_hash}"

        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            import json

            data = json.loads(cached)
            data["cached"] = True
            return SentimentResponse(**data)

        start = time.time()
        result = model_loader.sentiment(request.text)[0]
        latency_ms = int((time.time() - start) * 1000)

        response = SentimentResponse(
            label=result["label"],
            score=round(result["score"], 4),
            model="distilbert-base-uncased-finetuned-sst-2-english",
            latency_ms=latency_ms,
            cached=False,
        )

        import json

        await redis.setex(
            cache_key, CACHE_TTL_INFERENCE, json.dumps(response.model_dump())
        )

        return response


sentiment_service = SentimentService()
