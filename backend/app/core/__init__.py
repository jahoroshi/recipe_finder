"""Core package for external integrations and utilities."""

from app.core.gemini_client import GeminiClient, get_gemini_client

__all__ = ["GeminiClient", "get_gemini_client"]
