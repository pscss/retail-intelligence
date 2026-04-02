"""Sentiment analysis router."""

from fastapi import APIRouter, HTTPException, status

from inference_service.exceptions import ModelNotLoadedError
from inference_service.schemas.request import InferenceRequest
from inference_service.schemas.response import SentimentResponse
from inference_service.services.sentiment import sentiment_service
from shared.schemas.error import ErrorResponse

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.post("", response_model=SentimentResponse)
async def analyze_sentiment(request: InferenceRequest) -> SentimentResponse:
    """Analyze sentiment of input text."""
    try:
        return await sentiment_service.analyze(request)
    except ModelNotLoadedError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error="model_not_loaded",
                detail=e.message,
                service=e.service,
            ).model_dump(),
        ) from e
