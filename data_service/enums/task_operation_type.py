"""Task operation type enum."""

from enum import StrEnum


class TaskOperationType(StrEnum):
    """GraphQL operation type for the task."""

    QUERY = "QUERY"
    MUTATION = "MUTATION"
