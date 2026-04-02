"""Intent classification service."""

import hashlib
import json
import time

from constants import CACHE_TTL_INFERENCE

from inference_service.model_loader import model_loader
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import IntentResponse
from shared.redis_client import get_redis

INTENT_LABELS = [
    "delivery",
    "return",
    "refund",
    "complaint",
    "product_query",
    "cancellation",
    "payment",
    "account",
    "promotion",
    "feedback",
]


class IntentService:
    """Handles intent classification inference."""

    async def classify(self, request: InferenceRequest) -> IntentResponse:
        """Classify customer query intent, check cache first."""
        input_hash = hashlib.sha256(request.text.encode()).hexdigest()
        cache_key = f"inference:intent:{input_hash}"

        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["cached"] = True
            return IntentResponse(**data)

        start = time.time()
        result = model_loader.intent(request.text, candidate_labels=INTENT_LABELS)
        latency_ms = int((time.time() - start) * 1000)

        top_label = result["labels"][0]
        top_score = round(result["scores"][0], 4)
        all_scores = {
            label: round(score, 4)
            for label, score in zip(result["labels"], result["scores"], strict=True)
        }

        response = IntentResponse(
            label=top_label,
            score=top_score,
            model="cross-encoder/nli-MiniLM2-L6-H768",
            latency_ms=latency_ms,
            cached=False,
            all_scores=all_scores,
        )

        await redis.setex(
            cache_key, CACHE_TTL_INFERENCE, json.dumps(response.model_dump())
        )

        return response


intent_service = IntentService()
