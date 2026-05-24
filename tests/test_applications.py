from pathlib import Path


def test_example_applications_use_agent_runtime():
    for path in Path("applications").glob("*/app.py"):
        text = path.read_text(encoding="utf-8")
        if "benchmark_app" in str(path) or "web_dashboard" in str(path):
            continue
        assert "AgentRuntime" in text or "ClawFlowApp" in text

