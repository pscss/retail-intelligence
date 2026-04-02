"""FAQ RAG router."""

from fastapi import APIRouter, HTTPException, status

from retrieval_service.exceptions import IndexNotBuiltError, SearchError
from retrieval_service.schemas.request import FAQRequest
from retrieval_service.schemas.response import FAQResponse
from retrieval_service.services.rag import rag_service
from shared.schemas.error import ErrorResponse

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("", response_model=FAQResponse)
async def query_faq(request: FAQRequest) -> FAQResponse:
    """Retrieve most relevant FAQ answers for a customer question."""
    try:
        return await rag_service.query(request)
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
