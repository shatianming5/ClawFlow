from __future__ import annotations

from clawflow.connectors.local_email import LocalEmailConnector
from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


class LocalEmailOutboxTool(BaseTool):
    name = "local_email_outbox"
    description = "Store an email in a local JSONL outbox; replaceable by SMTP or email API connector."
    risk_level = "medium"
    input_schema = {"to": "recipient", "subject": "subject", "body": "body"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        connector = LocalEmailConnector(context.settings.root_dir / "outputs" / "outbox")
        result = connector.execute("send", args)
        return ToolResult(ok=True, data=result, artifacts=[result["outbox_path"]])

