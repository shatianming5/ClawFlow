from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from clawflow.core.schema import Plan
from clawflow.providers.base import PlanningProvider
from clawflow.providers.local_provider import DeterministicLocalProvider


class OpenAICompatibleProvider(PlanningProvider):
    """OpenAI-compatible JSON planner with deterministic local fallback."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback = DeterministicLocalProvider()

    def create_plan(self, user_input: str, context: dict[str, Any]) -> Plan:
        if not self.api_key:
            return self.fallback.create_plan(user_input, context)
        prompt = (
            "Create a JSON plan for ClawFlow. Return only JSON with goal and steps. "
            "Each step has id, action, args, depends_on, retry, description. "
            f"Available tools: {context.get('tools', [])}. User task: {user_input}"
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            content = body["choices"][0]["message"]["content"]
            return Plan.from_dict(json.loads(content))
        except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError):
            return self.fallback.create_plan(user_input, context)

