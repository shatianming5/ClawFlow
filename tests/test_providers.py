from clawflow.providers.local_provider import DeterministicLocalProvider


def test_local_provider_creates_different_plans_for_different_tasks():
    provider = DeterministicLocalProvider()
    tools = ["list_files", "generate_project_summary", "delete_file_dry_run", "rag_answer", "local_document_search"]
    files = ["README.md", "docs/technical_report.md"]
    delete_plan = provider.create_plan("请删除临时文件", {"tools": tools, "files": files, "memory_hits": []})
    rag_plan = provider.create_plan("请根据 docs 回答核心创新点", {"tools": tools, "files": files, "memory_hits": []})
    assert {step.action for step in delete_plan.steps} != {step.action for step in rag_plan.steps}
    assert "delete_file_dry_run" in {step.action for step in delete_plan.steps}
    assert "rag_answer" in {step.action for step in rag_plan.steps}

