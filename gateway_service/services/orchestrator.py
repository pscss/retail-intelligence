"""Gateway orchestration for GraphQL operations."""

import asyncio
import hashlib

from data_service.enums.operation_type import OperationType
from data_service.enums.served_from import ServedFrom
from gateway_service.clients.data_client import data_client
from gateway_service.clients.inference_client import inference_client
from gateway_service.clients.retrieval_client import retrieval_client


async def _safe_log(coro) -> None:
    """Wrap a fire-and-forget coroutine so exceptions are logged, not dropped."""
    try:
        await coro
    except Exception as exc:
        print(f"[warn] query log failed: {exc}")


class GatewayOrchestrator:
    """Coordinates downstream services and async query logging."""

    async def sentiment(self, text: str) -> dict:
        result = await inference_client.sentiment(text)
        await self._log_async(
            operation=OperationType.SENTIMENT,
            text=text,
            result=result,
        )
        return result

    async def intent(self, text: str) -> dict:
        result = await inference_client.intent(text)
        await self._log_async(
            operation=OperationType.INTENT,
            text=text,
            result=result,
        )
        return result

    async def triage(self, text: str) -> dict:
        result = await inference_client.triage(text)
        await self._log_async(
            operation=OperationType.TRIAGE,
            text=text,
            result=result,
        )
        return result

    async def search(self, query: str, top_k: int) -> dict:
        result = await retrieval_client.search_products(query, top_k)
        await self._log_async(
            operation=OperationType.SEARCH,
            text=query,
            result=result,
        )
        return result

    async def rag(self, question: str, top_k: int) -> dict:
        result = await retrieval_client.query_faq(question, top_k)
        await self._log_async(
            operation=OperationType.FAQ,
            text=question,
            result=result,
        )
        return result

    async def _log_async(
        self, operation: OperationType, text: str, result: dict
    ) -> None:
        """Fire-and-forget log write so client response is not blocked."""
        payload = {
            "operation": operation,
            "input_hash": hashlib.sha256(text.encode()).hexdigest(),
            "result_label": result.get("label"),
            "confidence": result.get("score"),
            "latency_ms": result.get("latency_ms"),
            "served_from": (
                ServedFrom.CACHE if result.get("cached") else ServedFrom.MODEL
            ),
        }
        asyncio.create_task(_safe_log(data_client.create_query_log(payload)))


gateway_orchestrator = GatewayOrchestrator()
