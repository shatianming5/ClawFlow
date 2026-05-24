from fastapi.testclient import TestClient

from clawflow.core.runtime import AgentRuntime
from clawflow.gateway.api import app
from clawflow.observability.metrics import MetricsStore


def test_policy_store_updates_effective_runtime_policy():
    runtime = AgentRuntime()
    runtime.policy_store.set_decision("high", "ask", "pytest governance override")
    refreshed = AgentRuntime()
    assert refreshed.policy.export()["high"] == "ask"
    rows = refreshed.policy_store.list(refreshed.settings.policy)
    assert any(row["risk_level"] == "high" and row["source"] == "sqlite_override" for row in rows)


def test_tool_usage_heatmap_reads_tool_call_trace_events():
    runtime = AgentRuntime()
    runtime.run("请分析当前项目结构，生成项目摘要。", application="test_tool_usage", auto_approve=True)
    usage = MetricsStore(runtime.settings.database_path).tool_usage()
    assert usage["total_tool_calls"] >= 1
    assert any(item["tool"] == "list_files" for item in usage["tools"])


def test_governance_api_and_tool_usage_api_work():
    client = TestClient(app)
    response = client.post("/governance/policy", json={"risk_level": "medium", "decision": "ask", "reason": "pytest"})
    assert response.status_code == 200
    assert response.json()["effective"]["medium"] == "ask"
    heatmap = client.get("/metrics/tool-usage")
    assert heatmap.status_code == 200
    assert "total_tool_calls" in heatmap.json()
