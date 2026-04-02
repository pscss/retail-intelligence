"""Shared utilities across all services."""

from shared.config import get_settings

settings = get_settings()

__all__ = ["settings", "get_settings"]
