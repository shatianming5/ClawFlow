from pathlib import Path

from clawflow.core.runtime import AgentRuntime


def test_multi_agent_flow_works():
    result = AgentRuntime().run("请让多个智能体协作完成一次项目分析。", application="test_multi_agent", auto_approve=True)
    assert result.status == "completed"
    assert Path("outputs/multi_agent_report.md").exists()

