"""Product semantic search service."""

import hashlib
import json
import time

from constants import CACHE_TTL_EMBEDDING

from retrieval_service.exceptions import SearchError
from retrieval_service.schemas.request import SearchRequest
from retrieval_service.schemas.response import ProductResult, SearchResponse
from retrieval_service.semantic_index import product_index
from shared.redis_client import get_redis


class SearchService:
    """Handles semantic product search."""

    async def search(self, request: SearchRequest) -> SearchResponse:
        """Search products semantically, check cache first."""
        input_hash = hashlib.sha256(
            f"{request.query}:{request.top_k}".encode()
        ).hexdigest()
        cache_key = f"search:products:{input_hash}"

        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            data = json.loads(cached)
            data["cached"] = True
            return SearchResponse(**data)

        start = time.time()
        try:
            raw_results = product_index.search(request.query, request.top_k)
        except Exception as e:
            raise SearchError(
                message=f"Product search failed: {e}",
                service="retrieval_service",
            ) from e
        latency_ms = int((time.time() - start) * 1000)

        results = [
            ProductResult(
                product_id=doc.get("product_id", str(i)),
                commodity_desc=doc.get("commodity_desc", ""),
                department=doc.get("department"),
                similarity_score=round(score, 4),
            )
            for i, (doc, score) in enumerate(raw_results)
        ]

        response = SearchResponse(
            query=request.query,
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


search_service = SearchService()
