"""Model loader — loads all transformer models at startup."""

import time

from transformers import pipeline

from inference_service.exceptions import ModelNotLoadedError


class ModelLoader:
    """Loads and caches all transformer models."""

    def __init__(self) -> None:
        self._sentiment_model = None
        self._intent_model = None
        self._triage_model = None
        self._loaded = False

    def load_all(self) -> None:
        """Load all models into memory. Called once at startup."""
        print("Loading sentiment model...")
        start = time.time()
        self._sentiment_model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True,
            max_length=512,
        )
        print(f"Sentiment model loaded in {time.time() - start:.2f}s")

        print("Loading intent model...")
        start = time.time()
        self._intent_model = pipeline(
            "zero-shot-classification",
            model="cross-encoder/nli-MiniLM2-L6-H768",
            truncation=True,
        )
        print(f"Intent model loaded in {time.time() - start:.2f}s")

        print("Loading triage model...")
        start = time.time()
        self._triage_model = pipeline(
            "zero-shot-classification",
            model="cross-encoder/nli-MiniLM2-L6-H768",
            truncation=True,
        )
        print(f"Triage model loaded in {time.time() - start:.2f}s")

        self._loaded = True
        print("All models loaded.")

    @property
    def sentiment(self):
        """Get sentiment model."""
        if not self._sentiment_model:
            raise ModelNotLoadedError(
                message="Sentiment model not loaded",
                service="inference_service",
            )
        return self._sentiment_model

    @property
    def intent(self):
        """Get intent model."""
        if not self._intent_model:
            raise ModelNotLoadedError(
                message="Intent model not loaded",
                service="inference_service",
            )
        return self._intent_model

    @property
    def triage(self):
        """Get triage model."""
        if not self._triage_model:
            raise ModelNotLoadedError(
                message="Triage model not loaded",
                service="inference_service",
            )
        return self._triage_model

    @property
    def is_loaded(self) -> bool:
        """Check if all models are loaded."""
        return self._loaded


model_loader = ModelLoader()
