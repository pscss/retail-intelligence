"""Base exception — all service exceptions inherit from this."""


class RetailIntelligenceError(Exception):
    """Base exception for all retail intelligence services."""

    def __init__(self, message: str, service: str | None = None) -> None:
        self.message = message
        self.service = service
        super().__init__(message)
