"""Inference service exceptions."""

from shared.exceptions import RetailIntelligenceError


class ModelNotLoadedError(RetailIntelligenceError):
    """Raised when a model is not loaded yet."""


class InferenceTimeoutError(RetailIntelligenceError):
    """Raised when inference takes too long."""


class UnsupportedTaskError(RetailIntelligenceError):
    """Raised when an unsupported task is requested."""


class LowConfidenceError(RetailIntelligenceError):
    """Raised when model confidence is below threshold."""
