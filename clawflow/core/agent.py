from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AgentRole:
    name: str
    responsibility: str

