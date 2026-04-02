"""Product search router."""

from fastapi import APIRouter, HTTPException, status

from retrieval_service.exceptions import IndexNotBuiltError, SearchError
from retrieval_service.schemas.request import SearchRequest
from retrieval_service.schemas.response import SearchResponse
from retrieval_service.services.search import search_service
from shared.schemas.error import ErrorResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_products(request: SearchRequest) -> SearchResponse:
    """Semantic product search over dunnhumby catalogue."""
    try:
        return await search_service.search(request)
    except IndexNotBuiltError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="index_not_built",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
    except SearchError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="search_failed",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
