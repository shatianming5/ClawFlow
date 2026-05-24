# Developer Guide

To add a tool, subclass `BaseTool`, define `name`, `description`, `risk_level`, schemas and `run(args, context)`, then register it in `ToolRegistry` or a plugin manifest. To add an application, call `AgentRuntime().run(task, application=...)`.
