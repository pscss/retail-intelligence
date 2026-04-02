"""Data service exceptions."""

from shared.exceptions import RetailIntelligenceError


class ProductNotFoundError(RetailIntelligenceError):
    """Raised when a product does not exist."""


class FAQNotFoundError(RetailIntelligenceError):
    """Raised when a FAQ does not exist."""


class TaskNotFoundError(RetailIntelligenceError):
    """Raised when a task does not exist in the registry."""


class TaskInactiveError(RetailIntelligenceError):
    """Raised when a task exists but is marked inactive."""


class DuplicateProductError(RetailIntelligenceError):
    """Raised when a product_id already exists."""


class SeedError(RetailIntelligenceError):
    """Raised when a seed operation fails."""
