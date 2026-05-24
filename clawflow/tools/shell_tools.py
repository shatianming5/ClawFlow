from __future__ import annotations

import shlex
import subprocess

from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


DANGEROUS_TOKENS = {"rm", "del", "format", "shutdown", "sudo", "chmod", "chown", "powershell", "curl", "wget"}


class ShellCommandTool(BaseTool):
    name = "shell_command"
    description = "Run a small whitelist of read-only or diagnostic shell commands."
    risk_level = "medium"
    input_schema = {"command": "shell command string"}

    def _is_allowed(self, command: str, allowlist: list[str]) -> tuple[bool, str]:
        try:
            parts = shlex.split(command)
        except ValueError as exc:
            return False, str(exc)
        if not parts:
            return False, "empty command"
        lowered = {part.lower() for part in parts}
        if lowered & DANGEROUS_TOKENS:
            return False, f"dangerous token blocked: {sorted(lowered & DANGEROUS_TOKENS)}"
        first = parts[0].lower()
        exact = " ".join(parts[:2]).lower() if len(parts) >= 2 else first
        allowed = {item.lower() for item in allowlist}
        if first in allowed or exact in allowed:
            return True, "allowed by whitelist"
        return False, f"command is not in whitelist: {first}"

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        command = str(args.get("command", ""))
        ok, reason = self._is_allowed(command, context.settings.shell_allowlist)
        if not ok:
            return ToolResult(ok=False, error=reason, metadata={"blocked": True})
        completed = subprocess.run(
            shlex.split(command),
            cwd=context.settings.root_dir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        return ToolResult(
            ok=completed.returncode == 0,
            data={"stdout": completed.stdout, "stderr": completed.stderr, "returncode": completed.returncode},
            error=completed.stderr if completed.returncode else "",
        )

