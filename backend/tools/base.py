"""
ROAM — Tool Base Class
All tools inherit from this and get automatic timing, error handling, and result tracking.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from schemas.models import ToolCall, ToolStatus


class ToolBase(ABC):
    """Abstract base class for all ROAM travel tools."""

    name: str = "base_tool"
    description: str = ""
    timeout_seconds: float = 10.0

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool logic. Subclasses must implement this."""
        ...

    def run(self, **kwargs: Any) -> tuple[Any, ToolCall]:
        """
        Run the tool with automatic timing, error handling, and ToolCall tracking.
        Returns (result, tool_call_record).
        """
        start = time.time()
        tool_call = ToolCall(
            tool_name=self.name,
            arguments={k: str(v)[:200] for k, v in kwargs.items()},  # Truncate for safety
        )

        try:
            result = self.execute(**kwargs)
            elapsed = (time.time() - start) * 1000
            tool_call.status = ToolStatus.SUCCESS
            tool_call.duration_ms = elapsed
            tool_call.result_summary = self._summarize(result)
            return result, tool_call

        except TimeoutError:
            tool_call.status = ToolStatus.TIMEOUT
            tool_call.duration_ms = (time.time() - start) * 1000
            tool_call.error = f"Tool timed out after {self.timeout_seconds}s"
            return None, tool_call

        except Exception as e:
            tool_call.status = ToolStatus.ERROR
            tool_call.duration_ms = (time.time() - start) * 1000
            tool_call.error = str(e)[:500]
            return None, tool_call

    def _summarize(self, result: Any) -> str:
        """Create a brief summary of the tool result."""
        if result is None:
            return "No result"
        if isinstance(result, list):
            return f"Returned {len(result)} items"
        if isinstance(result, dict):
            return f"Returned dict with {len(result)} keys"
        return str(result)[:200]
