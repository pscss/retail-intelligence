"""GraphQL query resolvers."""

import strawberry

from gateway_service.clients.retrieval_client import retrieval_client
from gateway_service.graphql.types import FAQResultType, ProductResultType


@strawberry.type
class Query:
    """Read-only gateway queries."""

    @strawberry.field
    def health(self) -> str:
        """Simple health query for GraphQL clients."""
        return "healthy"

    @strawberry.field
    async def search_products(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[ProductResultType]:
        """Semantic product search over dunnhumby catalogue."""
        response = await retrieval_client.search_products(query, top_k)
        return [
            ProductResultType(
                product_id=r["product_id"],
                commodity_desc=r["commodity_desc"],
                department=r.get("department"),
                similarity_score=r["similarity_score"],
            )
            for r in response.get("results", [])
        ]

    @strawberry.field
    async def query_faq(
        self,
        question: str,
        top_k: int = 3,
    ) -> list[FAQResultType]:
        """Retrieve most relevant FAQ answers."""
        response = await retrieval_client.query_faq(question, top_k)
        return [
            FAQResultType(
                question=r["question"],
                answer=r["answer"],
                intent_label=r.get("intent_label"),
                similarity_score=r["similarity_score"],
            )
            for r in response.get("results", [])
        ]
