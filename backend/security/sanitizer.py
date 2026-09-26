"""
ROAM — Input Sanitizer
Cleans and validates user input and external content.
"""

from __future__ import annotations

import re
import html


def sanitize_user_input(text: str, max_length: int = 2000) -> str:
    """Sanitize user input — remove dangerous patterns while keeping natural language."""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Escape HTML entities
    text = html.escape(text, quote=True)
    
    # Remove null bytes
    text = text.replace("\x00", "")
    
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    # Remove control characters except newlines
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    
    return text


def sanitize_external_content(text: str, max_length: int = 5000) -> str:
    """
    Sanitize content retrieved from external sources (web, APIs).
    More aggressive than user input sanitization.
    """
    if not text:
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Strip HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    
    # Remove script content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove URLs that could be tracking/malicious
    text = re.sub(r"javascript:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"data:", "", text, flags=re.IGNORECASE)
    
    # Escape HTML entities
    text = html.escape(text, quote=True)
    
    # Remove null bytes and control characters
    text = text.replace("\x00", "")
    text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def validate_input_length(text: str, max_length: int = 2000) -> tuple[bool, str]:
    """Validate input length."""
    if len(text) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters"
    if len(text.strip()) < 5:
        return False, "Input is too short to be a valid travel request"
    return True, "OK"
