from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ConnectorBase(ABC):
    """MCP-like connector boundary for replacing local adapters with real services."""

    name = "connector"

    @abstractmethod
    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

