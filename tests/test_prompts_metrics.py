from clawflow.core.runtime import AgentRuntime
from clawflow.observability.metrics import MetricsStore


def test_prompt_template_registry_persists_and_renders():
    runtime = AgentRuntime()
    runtime.prompts.upsert("pytest_prompt", "Hello {name}", "pytest template", "test")
    rendered = runtime.prompts.render("pytest_prompt", {"name": "ClawFlow"})
    assert rendered == "Hello ClawFlow"
    item = runtime.prompts.get("pytest_prompt")
    assert item["usage_count"] >= 1


def test_metrics_cost_and_failure_analysis_read_persisted_data():
    runtime = AgentRuntime()
    runtime.run("请删除 workspace 中的临时文件。", application="test_metrics_pending", auto_approve=False)
    metrics = MetricsStore(runtime.settings.database_path)
    summary = metrics.summary()
    cost = metrics.cost_summary()
    failures = metrics.failure_analysis()
    assert summary["total_runs"] >= 1
    assert "total_estimated_tokens" in cost
    assert failures["failed_or_pending_runs"]

