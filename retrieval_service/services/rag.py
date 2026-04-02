"""FAQ RAG service."""

import hashlib
import json
import time

from constants import CACHE_TTL_EMBEDDING

from retrieval_service.exceptions import SearchError
from retrieval_service.schemas.request import FAQRequest
from retrieval_service.schemas.response import FAQResponse, FAQResult
from retrieval_service.semantic_index import faq_index
from shared.redis_client import get_redis


class RAGService:
    """Handles FAQ retrieval augmented generation."""

    async def query(self, request: FAQRequest) -> FAQResponse:
        """Retrieve most relevant FAQ answers, check cache first."""
        input_hash = hashlib.sha256(
            f"{request.question}:{request.top_k}".encode()
        ).hexdigest()
        cache_key = f"rag:faqs:{input_hash}"

        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["cached"] = True
            return FAQResponse(**data)

        start = time.time()
        try:
            raw_results = faq_index.search(request.question, request.top_k)
        except Exception as e:
            raise SearchError(
                message=f"FAQ search failed: {e}",
                service="retrieval_service",
            ) from e
        latency_ms = int((time.time() - start) * 1000)

        results = [
            FAQResult(
                question=doc.get("question", ""),
                answer=doc.get("answer", ""),
                intent_label=doc.get("intent_label"),
                similarity_score=round(score, 4),
            )
            for doc, score in raw_results
        ]

        response = FAQResponse(
            question=request.question,
            results=results,
            total_results=len(results),
            model="all-MiniLM-L6-v2",
            latency_ms=latency_ms,
            cached=False,
        )

        await redis.setex(
            cache_key,
            CACHE_TTL_EMBEDDING,
            json.dumps(response.model_dump()),
        )

        return response


rag_service = RAGService()
