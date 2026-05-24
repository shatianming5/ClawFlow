from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from clawflow.gateway import web
from scripts._visual import draw_panel


def _run_cli(args: list[str]) -> str:
    completed = subprocess.run([sys.executable, "-m", "clawflow.gateway.cli", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return completed.stdout


def _html_text(page: str) -> list[str]:
    text = re.sub(r"<style.*?</style>", "", page, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return [text[i : i + 130] for i in range(0, min(len(text), 1500), 130)]


def _server_ready(base_url: str) -> bool:
    try:
        urlopen(f"{base_url}/health", timeout=1).read()
        return True
    except Exception:
        return False


def _capture_with_playwright(pages: dict[str, str], base_url: str = "http://127.0.0.1:8000") -> set[str]:
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return set()
    if not _server_ready(base_url):
        return set()
    captured: set[str] = set()
    route_map = {
        "web_home.png": "/dashboard",
        "web_run_agent.png": "/run-agent",
        "web_trace_timeline.png": "/trace-timeline",
        "web_tools.png": "/tools-page",
        "web_memory.png": "/memory-browser",
        "web_plugins.png": "/plugins-page",
        "web_benchmark.png": "/benchmark-page",
        "web_evaluation_leaderboard.png": "/evaluation-leaderboard",
        "web_governance.png": "/governance-page",
        "web_approvals.png": "/approvals-page",
        "web_prompts.png": "/prompts-page",
        "web_cost_dashboard.png": "/cost-page",
        "web_failure_analysis.png": "/failure-analysis",
        "web_failure_recovery.png": "/failure-recovery",
        "web_tool_usage_heatmap.png": "/tool-usage",
        "web_template_generator.png": "/template-generator",
        "web_audit_log.png": "/audit-log",
        "web_workflow_graph.png": "/workflow-graph",
        "web_multi_agent.png": "/multi-agent-page",
        "web_rag.png": "/rag-page",
        "web_applications.png": "/applications-page",
    }
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            for filename in pages:
                route = route_map.get(filename)
                if not route:
                    continue
                page.goto(base_url + route, wait_until="networkidle", timeout=5000)
                page.screenshot(path=f"docs/assets/screenshots/{filename}", full_page=True)
                captured.add(filename)
            browser.close()
    except Exception:
        return captured
    return captured


def main() -> None:
    Path("docs/assets/screenshots").mkdir(parents=True, exist_ok=True)
    cli_outputs = {
        "cli_research_application.png": _run_cli(["app", "research"]),
        "cli_trace_demo.png": _run_cli(["trace", "list"]),
        "cli_multi_agent_application.png": _run_cli(["app", "multi-agent"]),
        "cli_benchmark_demo.png": _run_cli(["benchmark"]),
    }
    for filename, output in cli_outputs.items():
        lines = output.splitlines()[:28]
        draw_panel(f"docs/assets/screenshots/{filename}", filename.replace("_", " ").replace(".png", ""), ["$ clawflow ...", *lines])

    pages = {
        "web_home.png": web.home_page(),
        "web_run_agent.png": web.run_agent_page(),
        "web_trace_timeline.png": web.trace_page(),
        "web_tools.png": web.tools_page(),
        "web_memory.png": web.memory_page(),
        "web_plugins.png": web.plugins_page(),
        "web_benchmark.png": web.benchmark_page(),
        "web_evaluation_leaderboard.png": web.evaluation_page(),
        "web_governance.png": web.governance_page(),
        "web_approvals.png": web.approvals_page(),
        "web_prompts.png": web.prompts_page(),
        "web_cost_dashboard.png": web.cost_page(),
        "web_failure_analysis.png": web.failure_page(),
        "web_failure_recovery.png": web.recovery_page(),
        "web_tool_usage_heatmap.png": web.tool_usage_page(),
        "web_template_generator.png": web.template_generator_page(),
        "web_audit_log.png": web.audit_page(),
        "web_workflow_graph.png": web.workflow_page(),
        "web_multi_agent.png": web.multi_agent_page(),
        "web_rag.png": web.rag_page(),
        "web_applications.png": web.applications_page(),
    }
    html_dir = Path("docs/assets/screenshots/html")
    html_dir.mkdir(parents=True, exist_ok=True)
    captured = _capture_with_playwright(pages)
    method = "playwright" if captured else "html_panel_fallback"
    for filename, page in pages.items():
        (html_dir / filename.replace(".png", ".html")).write_text(page, encoding="utf-8")
        if filename not in captured:
            draw_panel(f"docs/assets/screenshots/{filename}", filename.replace("_", " ").replace(".png", ""), _html_text(page))
        print(f"generated docs/assets/screenshots/{filename}")
    Path("docs/assets/screenshots/screenshot_method.txt").write_text(
        f"method={method}\nplaywright_captured={sorted(captured)}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
