from fastapi.testclient import TestClient

from clawflow.core.runtime import AgentRuntime
from clawflow.gateway.api import app


def test_approval_store_api_approve_resumes_pending_run():
    runtime = AgentRuntime()
    pending = runtime.run("请删除 workspace 中的临时文件。", application="test_approval_api", auto_approve=False)
    assert pending.status == "pending_approval"
    assert runtime.approvals.get_pending(pending.run_id)
    client = TestClient(app)
    response = client.post(f"/approvals/{pending.run_id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert not AgentRuntime().approvals.get_pending(pending.run_id)


def test_approval_deny_records_failed_run():
    runtime = AgentRuntime()
    pending = runtime.run("请删除 workspace 中的临时文件。", application="test_approval_deny", auto_approve=False)
    result = runtime.deny(pending.run_id)
    assert result.status == "failed"
    run = runtime.trace.get_run(pending.run_id)
    assert run["status"] == "failed"

