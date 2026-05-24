from __future__ import annotations

from clawflow.connectors.local_calendar import LocalCalendarConnector
from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


class LocalCalendarStoreTool(BaseTool):
    name = "local_calendar_store"
    description = "Store a calendar event locally; replaceable by Google Calendar or CalDAV connector."
    risk_level = "medium"
    input_schema = {"title": "event title", "date": "date", "notes": "notes"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        connector = LocalCalendarConnector(context.settings.root_dir / "outputs" / "calendar")
        result = connector.execute("create_event", args)
        return ToolResult(ok=True, data=result, artifacts=[result["events_path"]])

