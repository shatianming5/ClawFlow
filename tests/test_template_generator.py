import importlib.util
import json
from pathlib import Path

from scripts.create_application_template import create_application
from scripts.create_connector_template import create_connector
from scripts.create_tool_template import create_tool


def test_template_generators_create_runtime_backed_files(tmp_path):
    app_dir = create_application("pytest_template_app", "请生成一个测试模板任务。", tmp_path / "applications")
    tool_path = create_tool("pytest_template_tool", "low", tmp_path / "tools")
    assert (app_dir / "app.py").exists()
    assert "ClawFlowApp" in (app_dir / "app.py").read_text(encoding="utf-8")
    assert tool_path.exists()
    assert "BaseTool" in tool_path.read_text(encoding="utf-8")


def test_connector_template_generates_local_persistent_connector(tmp_path):
    connector_path = create_connector("pytest_ticket_connector", "sync_ticket", tmp_path / "connectors")
    text = connector_path.read_text(encoding="utf-8")
    assert "ConnectorBase" in text
    assert "events.jsonl" in text
    assert "local_jsonl" in text

    spec = importlib.util.spec_from_file_location("pytest_ticket_connector", connector_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    connector = module.PytestTicketConnectorConnector(output_dir=tmp_path / "out" / "ticket")
    result = connector.execute("sync_ticket", {"case_id": "C-001", "status": "open"})
    events_path = Path(result["events_path"])
    assert events_path.exists()
    event = json.loads(events_path.read_text(encoding="utf-8").strip())
    assert event["operation"] == "sync_ticket"
    assert event["payload"]["case_id"] == "C-001"
    assert event["adapter"] == "local_jsonl"
