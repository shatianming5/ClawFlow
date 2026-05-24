from __future__ import annotations

import json
from pathlib import Path

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
except ImportError as exc:  # pragma: no cover - import-time guidance
    raise RuntimeError("FastAPI is required for clawflow.gateway.api. Run `make install`.") from exc

from clawflow.config.settings import load_settings
from clawflow.core.runtime import AgentRuntime
from clawflow.gateway import web
from clawflow.observability.metrics import MetricsStore
from scripts.create_application_template import create_application
from scripts.create_connector_template import create_connector
from scripts.create_tool_template import create_tool


settings = load_settings()
app = FastAPI(title="ClawFlow Agent Runtime", version="0.1.0")
for mount_path, directory in [
    ("/docs/assets", settings.root_dir / "docs" / "assets"),
    ("/outputs", settings.root_dir / "outputs"),
]:
    Path(directory).mkdir(parents=True, exist_ok=True)
    app.mount(mount_path, StaticFiles(directory=str(directory)), name=mount_path.strip("/").replace("/", "_"))


def rt() -> AgentRuntime:
    return AgentRuntime(load_settings())


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "runtime": "clawflow", "storage": str(settings.database_path)}


@app.post("/run")
async def run(payload: dict) -> dict:
    result = rt().run(payload.get("task", ""), application=payload.get("application", "api"), auto_approve=bool(payload.get("auto_approve", False)))
    return result.to_dict()


@app.get("/runs")
def runs() -> list[dict]:
    return rt().trace.list_runs(100)


@app.get("/runs/{run_id}")
def run_detail(run_id: str) -> dict:
    return rt().trace.get_run(run_id) or {}


@app.get("/runs/{run_id}/trace")
def run_trace(run_id: str) -> list[dict]:
    return rt().trace.get_events(run_id)


@app.post("/runs/{run_id}/resume")
def resume(run_id: str, payload: dict | None = None) -> dict:
    payload = payload or {}
    return rt().resume(run_id, auto_approve=bool(payload.get("auto_approve", False))).to_dict()


@app.get("/tools")
def tools() -> list[dict]:
    return rt().registry.list()


@app.get("/memory")
def memory() -> list[dict]:
    return rt().memory.list_memory(100)


@app.post("/memory")
async def memory_add(payload: dict) -> dict:
    memory_id = rt().memory.add_memory(payload.get("text", ""), payload.get("metadata", {"source": "api"}))
    return {"id": memory_id}


@app.get("/plugins")
def plugins() -> dict:
    path = settings.root_dir / "clawflow" / "tools" / "plugin_manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/benchmark")
def benchmark() -> dict:
    path = settings.root_dir / "outputs" / "benchmark_results.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "missing"}


@app.get("/evaluation")
def evaluation() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).evaluation_leaderboard()


@app.get("/failure-recovery")
def failure_recovery() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).recovery_report(runtime.settings.checkpoint_dir)


@app.get("/audit")
def audit() -> list[dict]:
    return rt().audit.list_events(100)


@app.get("/governance")
def governance() -> dict:
    runtime = rt()
    return {"effective": runtime.policy.export(), "rows": runtime.policy_store.list(runtime.settings.policy)}


@app.post("/governance/policy")
async def governance_policy(payload: dict) -> dict:
    runtime = rt()
    runtime.policy_store.set_decision(payload["risk_level"], payload["decision"], payload.get("reason", ""))
    return {"effective": runtime.policy_store.get_policy(runtime.settings.policy)}


@app.get("/approvals")
def approvals(status: str | None = None) -> list[dict]:
    return rt().approvals.list(status=status, limit=100)


@app.post("/approvals/{run_id}/approve")
def approval_approve(run_id: str) -> dict:
    return rt().approve(run_id).to_dict()


@app.post("/approvals/{run_id}/deny")
def approval_deny(run_id: str) -> dict:
    return rt().deny(run_id).to_dict()


@app.get("/metrics")
def metrics() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).summary()


@app.get("/cost")
def cost() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).cost_summary()


@app.get("/failures")
def failures() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).failure_analysis()


@app.get("/metrics/tool-usage")
def tool_usage() -> dict:
    runtime = rt()
    return MetricsStore(runtime.settings.database_path).tool_usage()


@app.get("/prompts")
def prompts() -> list[dict]:
    return rt().prompts.list()


@app.post("/prompts")
async def prompt_upsert(payload: dict) -> dict:
    prompt_id = rt().prompts.upsert(
        payload["name"],
        payload["template"],
        payload.get("description", ""),
        payload.get("tags", ""),
    )
    return {"id": prompt_id}


@app.post("/prompts/{name}/render")
async def prompt_render(name: str, payload: dict) -> dict:
    return {"name": name, "rendered": rt().prompts.render(name, payload.get("variables", {}))}


@app.get("/workflow")
def workflow() -> dict:
    files = sorted((settings.root_dir / "outputs").glob("workflow_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return json.loads(files[0].read_text(encoding="utf-8")) if files else {}


@app.get("/applications")
def applications() -> list[dict]:
    return [
        {"name": "research", "task": "project analysis", "runtime": "AgentRuntime"},
        {"name": "personal", "task": "daily plan", "runtime": "AgentRuntime"},
        {"name": "safe", "task": "delete dry-run", "runtime": "AgentRuntime"},
        {"name": "multi-agent", "task": "collaboration", "runtime": "AgentRuntime"},
        {"name": "rag", "task": "retrieval answer", "runtime": "AgentRuntime"},
        {"name": "plugin", "task": "dynamic tool", "runtime": "AgentRuntime"},
    ]


@app.post("/templates/app")
async def template_app(payload: dict) -> dict:
    name = payload.get("name", "generated_runtime_app")
    if not str(name).startswith("generated_"):
        name = f"generated_{name}"
    path = create_application(name, payload.get("task", "请基于 ClawFlow Runtime 执行一个可观测任务。"))
    return {"path": str(path)}


@app.post("/templates/tool")
async def template_tool(payload: dict) -> dict:
    path = create_tool(payload.get("name", "generated_tool"), payload.get("risk", "low"), Path("clawflow/tools/generated"))
    return {"path": str(path)}


@app.post("/templates/connector")
async def template_connector(payload: dict) -> dict:
    path = create_connector(
        payload.get("name", "generated_connector"),
        payload.get("operation", "sync"),
        Path("clawflow/connectors/generated"),
    )
    return {"path": str(path)}


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> str:
    return web.home_page()


@app.get("/run-agent", response_class=HTMLResponse)
def run_agent_get() -> str:
    return web.run_agent_page()


@app.post("/run-agent", response_class=HTMLResponse)
async def run_agent_post(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    task = form.get("task", [""])[0]
    auto_approve = "auto_approve" in form
    result = rt().run(task, application="web", auto_approve=auto_approve).to_dict()
    return web.run_agent_page(result)


@app.get("/runs-page", response_class=HTMLResponse)
def runs_html() -> str:
    return web.runs_page()


@app.get("/trace-timeline", response_class=HTMLResponse)
def trace_html(run_id: str | None = None) -> str:
    return web.trace_page(run_id)


@app.get("/memory-browser", response_class=HTMLResponse)
def memory_html() -> str:
    return web.memory_page()


@app.get("/tools-page", response_class=HTMLResponse)
def tools_html() -> str:
    return web.tools_page()


@app.get("/plugins-page", response_class=HTMLResponse)
def plugins_html() -> str:
    return web.plugins_page()


@app.get("/applications-page", response_class=HTMLResponse)
def applications_html() -> str:
    return web.applications_page()


@app.get("/benchmark-page", response_class=HTMLResponse)
def benchmark_html() -> str:
    return web.benchmark_page()


@app.get("/evaluation-leaderboard", response_class=HTMLResponse)
def evaluation_html() -> str:
    return web.evaluation_page()


@app.get("/governance-page", response_class=HTMLResponse)
def governance_html() -> str:
    return web.governance_page()


@app.post("/governance-page/policy", response_class=HTMLResponse)
async def governance_policy_html(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    runtime = rt()
    try:
        runtime.policy_store.set_decision(
            form.get("risk_level", ["high"])[0],
            form.get("decision", ["ask"])[0],
            form.get("reason", [""])[0],
        )
    except Exception:
        pass
    return web.governance_page()


@app.get("/approvals-page", response_class=HTMLResponse)
def approvals_html() -> str:
    return web.approvals_page()


@app.post("/approvals-page/{run_id}/approve", response_class=HTMLResponse)
def approval_approve_html(run_id: str) -> str:
    try:
        result = rt().approve(run_id)
        message = f"Approved {run_id}; status is now {result.status}."
    except Exception as exc:
        message = str(exc)
    return web.approvals_page(message)


@app.post("/approvals-page/{run_id}/deny", response_class=HTMLResponse)
def approval_deny_html(run_id: str) -> str:
    try:
        result = rt().deny(run_id)
        message = f"Denied {run_id}; status is now {result.status}."
    except Exception as exc:
        message = str(exc)
    return web.approvals_page(message)


@app.get("/prompts-page", response_class=HTMLResponse)
def prompts_html() -> str:
    return web.prompts_page()


@app.post("/prompts-page/render", response_class=HTMLResponse)
async def prompts_render_html(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    name = form.get("name", ["research_summary"])[0]
    variables_raw = form.get("variables", ["{}"])[0]
    try:
        variables = json.loads(variables_raw)
        rendered = rt().prompts.render(name, variables)
    except Exception as exc:
        rendered = f"Render failed: {exc}"
    return web.prompts_page(rendered)


@app.get("/cost-page", response_class=HTMLResponse)
def cost_html() -> str:
    return web.cost_page()


@app.get("/failure-analysis", response_class=HTMLResponse)
def failure_html() -> str:
    return web.failure_page()


@app.get("/failure-recovery", response_class=HTMLResponse)
def recovery_html() -> str:
    return web.recovery_page()


@app.get("/tool-usage", response_class=HTMLResponse)
def tool_usage_html() -> str:
    return web.tool_usage_page()


@app.get("/template-generator", response_class=HTMLResponse)
def template_generator_html() -> str:
    return web.template_generator_page()


@app.post("/template-generator/app", response_class=HTMLResponse)
async def template_generator_app_html(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    name = form.get("name", ["generated_runtime_app"])[0]
    if not name.startswith("generated_"):
        name = f"generated_{name}"
    path = create_application(name, form.get("task", ["请基于 ClawFlow Runtime 执行一个可观测任务。"])[0])
    return web.template_generator_page(f"Generated application template at {path}")


@app.post("/template-generator/tool", response_class=HTMLResponse)
async def template_generator_tool_html(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    path = create_tool(form.get("name", ["generated_tool"])[0], form.get("risk", ["low"])[0], Path("clawflow/tools/generated"))
    return web.template_generator_page(f"Generated tool template at {path}")


@app.post("/template-generator/connector", response_class=HTMLResponse)
async def template_generator_connector_html(request: Request) -> str:
    from urllib.parse import parse_qs

    raw = (await request.body()).decode("utf-8")
    form = parse_qs(raw)
    path = create_connector(
        form.get("name", ["generated_connector"])[0],
        form.get("operation", ["sync"])[0],
        Path("clawflow/connectors/generated"),
    )
    return web.template_generator_page(f"Generated connector template at {path}")


@app.get("/audit-log", response_class=HTMLResponse)
def audit_html() -> str:
    return web.audit_page()


@app.get("/workflow-graph", response_class=HTMLResponse)
def workflow_html() -> str:
    return web.workflow_page()


@app.get("/multi-agent-page", response_class=HTMLResponse)
def multi_agent_html() -> str:
    return web.multi_agent_page()


@app.get("/rag-page", response_class=HTMLResponse)
def rag_html() -> str:
    return web.rag_page()


@app.get("/roadmap", response_class=HTMLResponse)
def roadmap_html() -> str:
    return web.roadmap_page()
