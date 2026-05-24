from pathlib import Path

from scripts.create_application_template import create_application
from scripts.create_tool_template import create_tool


def test_template_generators_create_runtime_backed_files(tmp_path):
    app_dir = create_application("pytest_template_app", "请生成一个测试模板任务。", tmp_path / "applications")
    tool_path = create_tool("pytest_template_tool", "low", tmp_path / "tools")
    assert (app_dir / "app.py").exists()
    assert "ClawFlowApp" in (app_dir / "app.py").read_text(encoding="utf-8")
    assert tool_path.exists()
    assert "BaseTool" in tool_path.read_text(encoding="utf-8")
