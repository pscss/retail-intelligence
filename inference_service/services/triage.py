"""Complaint triage service."""

import hashlib
import json
import time

from constants import CACHE_TTL_INFERENCE

from inference_service.model_loader import model_loader
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import TriageResponse
from shared.redis_client import get_redis

SEVERITY_LABELS = ["LOW", "MEDIUM", "HIGH"]

CATEGORY_LABELS = [
    "delivery_issue",
    "product_defect",
    "billing_error",
    "customer_service",
    "refund_dispute",
    "account_issue",
]


class TriageService:
    """Handles complaint triage inference."""

    async def triage(self, request: InferenceRequest) -> TriageResponse:
        """Triage a complaint by severity and category."""
        input_hash = hashlib.sha256(request.text.encode()).hexdigest()
        cache_key = f"inference:triage:{input_hash}"

        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["cached"] = True
            return TriageResponse(**data)

        start = time.time()
        severity_result = model_loader.triage(
            request.text, candidate_labels=SEVERITY_LABELS
        )
        category_result = model_loader.triage(
            request.text, candidate_labels=CATEGORY_LABELS
        )
        latency_ms = int((time.time() - start) * 1000)

        response = TriageResponse(
            label=severity_result["labels"][0],
            score=round(severity_result["scores"][0], 4),
            model="cross-encoder/nli-MiniLM2-L6-H768",
            latency_ms=latency_ms,
            cached=False,
            category=category_result["labels"][0],
        )

        await redis.setex(
            cache_key, CACHE_TTL_INFERENCE, json.dumps(response.model_dump())
        )

        return response


triage_service = TriageService()
