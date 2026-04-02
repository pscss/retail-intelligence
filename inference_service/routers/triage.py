"""Complaint triage router."""

from fastapi import APIRouter, HTTPException, status

from inference_service.exceptions import ModelNotLoadedError
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import TriageResponse
from inference_service.services.triage import triage_service
from shared.schemas.error import ErrorResponse

router = APIRouter(prefix="/triage", tags=["triage"])


@router.post("", response_model=TriageResponse)
async def triage_complaint(request: InferenceRequest) -> TriageResponse:
    """Triage a complaint by severity and category."""
    try:
        return await triage_service.triage(request)
    except ModelNotLoadedError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="model_not_loaded",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
