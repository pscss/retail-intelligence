"""GraphQL mutation resolvers for gateway operations."""

import json

import strawberry
from pydantic import ValidationError
from strawberry.exceptions import GraphQLError

from gateway_service.graphql.types import (
    FAQResultType,
    InferenceResultType,
    IntentResultType,
    ProductResultType,
    RagResultType,
    SearchResultType,
    TriageResultType,
)
from gateway_service.schemas import RagInput, SearchInput, TextInput
from gateway_service.services.orchestrator import gateway_orchestrator


def _as_graphql_error(exc: Exception) -> GraphQLError:
    """Convert upstream errors into GraphQL-safe messages."""
    return GraphQLError(f"Gateway operation failed: {exc}")


def _as_validation_error(exc: ValidationError) -> GraphQLError:
    """Convert pydantic validation errors into GraphQL-safe messages."""
    return GraphQLError(f"Invalid input: {exc.errors()}")


@strawberry.type
class Mutation:
    """Mutations trigger compute operations with side-effects."""

    @strawberry.mutation
    async def sentiment(self, text: str) -> InferenceResultType:
        try:
            payload = TextInput(text=text)
            data = await gateway_orchestrator.sentiment(payload.text)
            return InferenceResultType(**data)
        except ValidationError as exc:
            raise _as_validation_error(exc) from exc
        except Exception as exc:
            raise _as_graphql_error(exc) from exc

    @strawberry.mutation
    async def intent(self, text: str) -> IntentResultType:
        try:
            payload = TextInput(text=text)
            data = await gateway_orchestrator.intent(payload.text)
            all_scores = data.get("all_scores")
            data["all_scores"] = json.dumps(all_scores) if all_scores else None
            return IntentResultType(**data)
        except ValidationError as exc:
            raise _as_validation_error(exc) from exc
        except Exception as exc:
            raise _as_graphql_error(exc) from exc

    @strawberry.mutation
    async def triage(self, text: str) -> TriageResultType:
        try:
            payload = TextInput(text=text)
            data = await gateway_orchestrator.triage(payload.text)
            return TriageResultType(**data)
        except ValidationError as exc:
            raise _as_validation_error(exc) from exc
        except Exception as exc:
            raise _as_graphql_error(exc) from exc

    @strawberry.mutation
    async def search(self, query: str, top_k: int = 5) -> SearchResultType:
        try:
            payload = SearchInput(query=query, top_k=top_k)
            data = await gateway_orchestrator.search(
                query=payload.query, top_k=payload.top_k
            )
            products = [ProductResultType(**item) for item in data["results"]]
            return SearchResultType(
                query=data["query"],
                total_results=data["total_results"],
                model=data["model"],
                latency_ms=data["latency_ms"],
                cached=data["cached"],
                results=products,
            )
        except ValidationError as exc:
            raise _as_validation_error(exc) from exc
        except Exception as exc:
            raise _as_graphql_error(exc) from exc

    @strawberry.mutation
    async def faq_rag(self, question: str, top_k: int = 3) -> RagResultType:
        try:
            payload = RagInput(question=question, top_k=top_k)
            data = await gateway_orchestrator.rag(
                question=payload.question, top_k=payload.top_k
            )
            faqs = [FAQResultType(**item) for item in data["results"]]
            return RagResultType(
                question=data["question"],
                total_results=data["total_results"],
                model=data["model"],
                latency_ms=data["latency_ms"],
                cached=data["cached"],
                results=faqs,
            )
        except ValidationError as exc:
            raise _as_validation_error(exc) from exc
        except Exception as exc:
            raise _as_graphql_error(exc) from exc
