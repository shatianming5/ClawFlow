from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from clawflow.core.schema import Plan


class PlanningProvider(ABC):
    @abstractmethod
    def create_plan(self, user_input: str, context: dict[str, Any]) -> Plan:
        raise NotImplementedError

