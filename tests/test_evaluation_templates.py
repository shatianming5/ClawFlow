from pathlib import Path

from fastapi.testclient import TestClient

from clawflow.core.runtime import AgentRuntime
from clawflow.gateway.api import app
from clawflow.observability.metrics import MetricsStore
from scripts.run_benchmark import main as benchmark_main


def test_evaluation_leaderboard_and_recovery_report_are_generated():
    benchmark_main()
    runtime = AgentRuntime()
    metrics = MetricsStore(runtime.settings.database_path)
    leaderboard = metrics.evaluation_leaderboard()
    recovery = metrics.recovery_report(runtime.settings.checkpoint_dir)
    assert leaderboard["leaderboard"]
    assert "recommendations" in recovery
    assert Path("outputs/evaluation_leaderboard.json").exists()
    assert Path("outputs/failure_recovery_report.md").exists()


def test_template_api_generates_runtime_backed_application_and_tool():
    client = TestClient(app)
    app_response = client.post("/templates/app", json={"name": "generated_pytest_api_app", "task": "请测试模板生成。"})
    tool_response = client.post("/templates/tool", json={"name": "generated_pytest_api_tool", "risk": "low"})
    assert app_response.status_code == 200
    assert tool_response.status_code == 200
    app_path = Path(app_response.json()["path"]) / "app.py"
    tool_path = Path(tool_response.json()["path"])
    assert app_path.exists()
    assert "ClawFlowApp" in app_path.read_text(encoding="utf-8")
    assert tool_path.exists()
    assert "BaseTool" in tool_path.read_text(encoding="utf-8")
