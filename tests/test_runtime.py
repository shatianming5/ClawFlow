from pathlib import Path

from clawflow.core.runtime import AgentRuntime


def test_runtime_can_run_local_task():
    result = AgentRuntime().run("请分析当前项目结构，生成项目摘要。", application="test_runtime", auto_approve=True)
    assert result.status == "completed"
    assert result.artifacts
    assert Path("outputs/research_summary.md").exists()
    assert AgentRuntime().trace.get_events(result.run_id)


def test_checkpoint_is_saved_and_resume_works():
    runtime = AgentRuntime()
    pending = runtime.run("请删除 workspace 中的临时文件。", application="test_resume", auto_approve=False)
    assert pending.status == "pending_approval"
    assert runtime.checkpoints.path_for(pending.run_id).exists()
    resumed = runtime.resume(pending.run_id, auto_approve=True)
    assert resumed.status == "completed"
    assert Path("outputs/delete_dry_run.md").exists()

