"""Intent classification router."""

from fastapi import APIRouter, HTTPException, status

from inference_service.exceptions import ModelNotLoadedError
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import IntentResponse
from inference_service.services.intent import intent_service
from shared.schemas.error import ErrorResponse

router = APIRouter(prefix="/intent", tags=["intent"])


@router.post("", response_model=IntentResponse)
async def classify_intent(request: InferenceRequest) -> IntentResponse:
    """Classify intent of customer query."""
    try:
        return await intent_service.classify(request)
    except ModelNotLoadedError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="model_not_loaded",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
