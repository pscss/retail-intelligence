"""Operation type enum."""

from enum import StrEnum


class OperationType(StrEnum):
    """Inference operation types."""

    SENTIMENT = "SENTIMENT"
    INTENT = "INTENT"
    TRIAGE = "TRIAGE"
    SEARCH = "SEARCH"
    FAQ = "FAQ"
