from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "ROADMAP.md",
    "CHANGELOG.md",
    "Dockerfile",
    "docker-compose.yml",
    "Makefile",
    ".env.example",
    ".github/workflows/ci.yml",
    "scripts/verify_deliverables.py",
    "scripts/package_release.py",
    "scripts/check_publish_readiness.py",
    "scripts/verify_submission_package.py",
    "docs/openapi.json",
    "docs/api_reference.md",
    "docs/github_publish_guide.md",
    "docs/delivery_checklist.md",
    "docs/defense_qa.md",
    "docs/comparison.md",
    "docs/technical_report.md",
    "docs/technical_report.docx",
    "docs/technical_report.pdf",
    "slides/ClawFlow_presentation.pptx",
    "slides/ClawFlow_presentation.pdf",
    "slides/ppt_outline.md",
    "slides/slide_notes.md",
    "outputs/benchmark_results.json",
    "outputs/evaluation_leaderboard.json",
    "outputs/failure_recovery_report.md",
    "outputs/release_manifest.md",
    "outputs/submission_package_manifest.md",
    "outputs/research_summary.md",
    "outputs/report_outline.md",
    "outputs/TODO.md",
    "outputs/daily_plan.md",
    "outputs/delete_dry_run.md",
    "outputs/multi_agent_report.md",
    "outputs/rag_answer.md",
    "outputs/plugin_workspace_stats.json",
]

REQUIRED_DIAGRAMS = [
    "architecture.png",
    "workflow.png",
    "tool_governance.png",
    "trace_lifecycle.png",
    "multi_agent_topology.png",
    "plugin_system.png",
    "rag_pipeline.png",
    "agentos_kernel.png",
    "example_application_stack.png",
]

REQUIRED_FIGURES = [
    "benchmark_latency.png",
    "benchmark_success_rate.png",
    "benchmark_tool_calls.png",
    "benchmark_trace_events.png",
    "evaluation_leaderboard.png",
    "failure_recovery_actions.png",
]

REQUIRED_SCREENSHOTS = [
    "cli_research_application.png",
    "cli_trace_demo.png",
    "cli_multi_agent_application.png",
    "cli_benchmark_demo.png",
    "web_home.png",
    "web_run_agent.png",
    "web_trace_timeline.png",
    "web_tools.png",
    "web_memory.png",
    "web_plugins.png",
    "web_benchmark.png",
    "web_evaluation_leaderboard.png",
    "web_governance.png",
    "web_approvals.png",
    "web_audit_log.png",
    "web_workflow_graph.png",
    "web_multi_agent.png",
    "web_rag.png",
    "web_applications.png",
    "web_prompts.png",
    "web_cost_dashboard.png",
    "web_failure_analysis.png",
    "web_failure_recovery.png",
    "web_tool_usage_heatmap.png",
    "web_template_generator.png",
]

README_KEYWORDS = [
    "Agent Runtime",
    "AgentOS Kernel",
    "Workflow Orchestration",
    "Checkpoint & Resume",
    "Tool Sandbox",
    "Permission Governance",
    "Memory Layer",
    "Observability",
    "Trace Replay",
    "Plugin Registry",
    "Human Approval Queue",
    "Prompt Template Registry",
    "Evaluation Leaderboard",
    "Failure Recovery Report",
    "Developer Framework",
    "GitHub Publish",
    "Why ClawFlow is not just demos",
]

APPLICATIONS = [
    "research_assistant",
    "personal_assistant",
    "safe_tool_call",
    "multi_agent_project_analysis",
    "rag_assistant",
    "plugin_tool_app",
    "trace_replay",
    "human_approval",
]


class VerificationError(AssertionError):
    pass


def _path(path: str | Path) -> Path:
    return ROOT / path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def require_files(paths: Iterable[str], min_size: int = 1) -> None:
    for path in paths:
        full = _path(path)
        require(full.exists(), f"missing file: {path}")
        require(full.stat().st_size >= min_size, f"file is too small: {path}")


def verify_files() -> None:
    require_files(REQUIRED_FILES)
    require_files([f"docs/assets/diagrams/{name}" for name in REQUIRED_DIAGRAMS], min_size=1000)
    require_files([f"docs/assets/figures/{name}" for name in REQUIRED_FIGURES], min_size=1000)
    require_files([f"docs/assets/screenshots/{name}" for name in REQUIRED_SCREENSHOTS], min_size=1000)
    require(_path("docs/assets/screenshots/screenshot_method.txt").exists(), "missing screenshot method record")


def verify_readme() -> None:
    text = _path("README.md").read_text(encoding="utf-8")
    for keyword in README_KEYWORDS:
        require(keyword in text, f"README missing keyword/section: {keyword}")
    require("demo.py" in text, "README should explicitly distinguish ClawFlow from demo.py projects")
    require("docs/openapi.json" in text, "README should mention OpenAPI export")


def verify_openapi() -> None:
    data = json.loads(_path("docs/openapi.json").read_text(encoding="utf-8"))
    paths = data.get("paths", {})
    require(len(paths) >= 20, f"OpenAPI path count too small: {len(paths)}")
    for route in ["/health", "/run", "/runs", "/tools", "/memory", "/benchmark", "/evaluation", "/failure-recovery"]:
        require(route in paths, f"OpenAPI missing route: {route}")


def verify_benchmark() -> None:
    benchmark = json.loads(_path("outputs/benchmark_results.json").read_text(encoding="utf-8"))
    require(benchmark.get("total_tasks", 0) >= 6, "benchmark should include at least six tasks")
    require(benchmark.get("success_rate", 0) >= 0.8, "benchmark success rate below expected threshold")
    require(benchmark.get("trace_event_count", 0) > 0, "benchmark must include trace events")
    leaderboard = json.loads(_path("outputs/evaluation_leaderboard.json").read_text(encoding="utf-8"))
    require(leaderboard.get("leaderboard"), "evaluation leaderboard is empty")
    recovery = json.loads(_path("outputs/failure_recovery_report.json").read_text(encoding="utf-8"))
    require("recommendations" in recovery, "failure recovery report missing recommendations")


def verify_applications() -> None:
    for app in APPLICATIONS:
        app_file = _path(f"applications/{app}/app.py")
        require(app_file.exists(), f"missing application app.py: {app}")
        text = app_file.read_text(encoding="utf-8")
        require("AgentRuntime" in text or "ClawFlowApp" in text, f"application does not use unified runtime: {app}")


def verify_tests() -> None:
    tests = sorted(_path("tests").glob("test_*.py"))
    require(len(tests) >= 15, f"expected broad test suite, found {len(tests)} files")


def verify_publish_readiness() -> None:
    from scripts.check_publish_readiness import build_report

    report = build_report()
    require(report["status"] in {"ready", "needs_remote", "ready_with_warnings"}, "publish readiness has errors")
    require(report["git_repository"], "publish readiness should run inside a git repository")
    require(report["required_assets"], "publish readiness did not check required assets")


def run_pytest() -> str:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    require(completed.returncode == 0, "pytest failed:\n" + completed.stdout)
    return completed.stdout


def main(run_tests: bool = False) -> dict:
    checks = [
        ("files", verify_files),
        ("readme", verify_readme),
        ("openapi", verify_openapi),
        ("benchmark", verify_benchmark),
        ("applications", verify_applications),
        ("tests", verify_tests),
        ("publish_readiness", verify_publish_readiness),
    ]
    passed: list[str] = []
    for name, fn in checks:
        fn()
        passed.append(name)
    pytest_output = ""
    if run_tests:
        pytest_output = run_pytest()
        passed.append("pytest")
    result = {"status": "ok", "passed": passed, "pytest": pytest_output.strip()}
    output = _path("outputs/deliverable_verification.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    run_tests = "--with-tests" in sys.argv
    try:
        print(json.dumps(main(run_tests=run_tests), ensure_ascii=False, indent=2))
    except VerificationError as exc:
        print(f"deliverable verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
