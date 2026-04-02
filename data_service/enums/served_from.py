"""Served from enum."""

from enum import StrEnum


class ServedFrom(StrEnum):
    """Where the result was served from."""

    MODEL = "MODEL"
    CACHE = "CACHE"
