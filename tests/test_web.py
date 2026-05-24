from clawflow.gateway import web


def test_web_ui_reads_real_persisted_data():
    html = web.memory_page()
    assert "Memory Browser" in html
    assert "SQLite-backed" in html
    assert "ClawFlow" in web.home_page()
    assert "Human Approval" in web.approvals_page()
    assert "Prompt Template Registry" in web.prompts_page()
    assert "Cost Dashboard" in web.cost_page()
    assert "Failure Analysis" in web.failure_page()
    assert "Evaluation Leaderboard" in web.evaluation_page()
    assert "Failure Recovery Report" in web.recovery_page()
    assert "Tool Usage Heatmap" in web.tool_usage_page()
    assert "Template Generator" in web.template_generator_page()
    assert "Connector Template" in web.template_generator_page()
