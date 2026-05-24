from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from clawflow.config.settings import load_settings
from clawflow.core.runtime import AgentRuntime
from clawflow.observability.metrics import MetricsStore


def runtime() -> AgentRuntime:
    return AgentRuntime(load_settings())


def css() -> str:
    return """
    :root { --bg:#0e1116; --panel:#171b22; --line:#2b323d; --text:#eef2f6; --muted:#99a4b3; --accent:#49d2b4; --warn:#f2b84b; --danger:#ff6b6b; }
    * { box-sizing:border-box; } body { margin:0; font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:var(--bg); color:var(--text); }
    a { color:inherit; text-decoration:none; } .shell { display:grid; grid-template-columns:250px 1fr; min-height:100vh; }
    nav { border-right:1px solid var(--line); padding:22px 16px; background:#11151b; position:sticky; top:0; height:100vh; }
    nav h1 { font-size:22px; margin:0 0 4px; } nav p { color:var(--muted); margin:0 0 18px; font-size:12px; line-height:1.4; }
    nav a { display:block; padding:9px 10px; border-radius:7px; color:#cbd5df; font-size:14px; margin:2px 0; } nav a:hover { background:#202733; }
    main { padding:24px; } .top { display:flex; gap:12px; align-items:flex-start; justify-content:space-between; margin-bottom:20px; }
    h2 { margin:0; font-size:24px; } .subtitle { color:var(--muted); margin-top:6px; max-width:900px; line-height:1.45; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; } .card { background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:16px; }
    .metric { font-size:28px; font-weight:750; } .label { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
    table { width:100%; border-collapse:collapse; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }
    th,td { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line); vertical-align:top; font-size:13px; } th { color:#d7dee8; background:#1d232d; }
    code,pre { background:#0b0d11; border:1px solid var(--line); border-radius:6px; } code { padding:2px 5px; } pre { padding:12px; overflow:auto; max-height:520px; }
    .pill { display:inline-block; padding:3px 8px; border-radius:999px; background:#26303b; color:#dbe7ef; font-size:12px; } .low { color:var(--accent); } .medium { color:var(--warn); } .high { color:var(--danger); }
    form { display:grid; gap:10px; max-width:850px; } textarea,input { width:100%; border:1px solid var(--line); background:#10141a; color:var(--text); border-radius:7px; padding:10px; font:inherit; }
    button { background:var(--accent); color:#04110e; border:0; border-radius:7px; padding:10px 14px; font-weight:700; width:max-content; cursor:pointer; }
    .danger-button { background:var(--danger); color:#1c0505; }
    .timeline { display:grid; gap:8px; } .event { border-left:3px solid var(--accent); padding:8px 12px; background:var(--panel); border-radius:0 7px 7px 0; }
    @media (max-width:800px){ .shell{grid-template-columns:1fr;} nav{height:auto;position:relative;border-right:0;border-bottom:1px solid var(--line);} }
    """


def layout(title: str, body: str) -> str:
    links = [
        ("Home", "/dashboard"),
        ("Run Agent", "/run-agent"),
        ("Runs", "/runs-page"),
        ("Trace Timeline", "/trace-timeline"),
        ("Memory", "/memory-browser"),
        ("Tools", "/tools-page"),
        ("Plugins", "/plugins-page"),
        ("Applications", "/applications-page"),
        ("Benchmark", "/benchmark-page"),
        ("Evaluation", "/evaluation-leaderboard"),
        ("Governance", "/governance-page"),
        ("Approvals", "/approvals-page"),
        ("Audit Log", "/audit-log"),
        ("Prompts", "/prompts-page"),
        ("Cost", "/cost-page"),
        ("Failures", "/failure-analysis"),
        ("Recovery", "/failure-recovery"),
        ("Tool Heatmap", "/tool-usage"),
        ("Templates", "/template-generator"),
        ("Workflow Graph", "/workflow-graph"),
        ("Multi-agent", "/multi-agent-page"),
        ("RAG", "/rag-page"),
        ("Roadmap", "/roadmap"),
    ]
    nav = "".join(f'<a href="{href}">{label}</a>' for label, href in links)
    return f"""
    <!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{html.escape(title)} · ClawFlow</title><style>{css()}</style></head>
    <body><div class="shell"><nav><h1>ClawFlow</h1><p>Agent Runtime · AgentOS Kernel · Governance · Trace Replay</p>{nav}</nav>
    <main>{body}</main></div></body></html>
    """


def header(title: str, subtitle: str) -> str:
    return f'<div class="top"><div><h2>{html.escape(title)}</h2><div class="subtitle">{html.escape(subtitle)}</div></div></div>'


def home_page() -> str:
    rt = runtime()
    runs = rt.trace.list_runs()
    tools = rt.registry.list()
    memories = rt.memory.list_memory()
    audits = rt.audit.list_events()
    metrics = MetricsStore(rt.settings.database_path).summary()
    body = header(
        "AgentOS Infrastructure Dashboard",
        "让智能体从能回答走向能执行、能记忆、能恢复、能协作、能治理。所有指标读取真实 SQLite、trace、memory 和输出文件。",
    )
    body += '<div class="grid">'
    for label, value in [
        ("Runs", len(runs)),
        ("Tools", len(tools)),
        ("Memories", len(memories)),
        ("Audit Events", len(audits)),
        ("Success Rate", metrics["success_rate"]),
        ("Pending Approval", metrics["pending_approval_runs"]),
    ]:
        body += f'<div class="card"><div class="label">{label}</div><div class="metric">{value}</div></div>'
    body += "</div>"
    body += '<div class="card" style="margin-top:14px"><h3>Infrastructure Story</h3><p>ClawFlow packages Planner, Executor, Tool Sandbox, Permission Governance, Memory Layer, Trace Replay, Plugin Registry, MCP-like Connector, RAG Module and Multi-agent Collaboration into a reusable developer-facing framework.</p></div>'
    return layout("Dashboard", body)


def run_agent_page(result: dict[str, Any] | None = None) -> str:
    body = header("Run Agent", "Trigger the unified AgentRuntime from the Web Gateway.")
    body += """
    <form method="post" action="/run-agent">
      <textarea name="task" rows="5">请分析当前项目结构，生成项目摘要、README 摘要、技术报告大纲和 TODO 列表。</textarea>
      <label><input type="checkbox" name="auto_approve" checked> Auto-approve local ask-level tools</label>
      <button type="submit">Run Agent</button>
    </form>
    """
    if result:
        body += f"<pre>{html.escape(json.dumps(result, ensure_ascii=False, indent=2))}</pre>"
    return layout("Run Agent", body)


def runs_page() -> str:
    rt = runtime()
    rows = "".join(
        f"<tr><td><a href='/trace-timeline?run_id={run['run_id']}'><code>{run['run_id']}</code></a></td><td>{html.escape(run['status'])}</td><td>{html.escape(str(run.get('application') or ''))}</td><td>{html.escape(run['user_input'][:120])}</td></tr>"
        for run in rt.trace.list_runs(100)
    )
    body = header("Runs", "Persisted run records from the trace database.")
    body += f"<table><tr><th>Run ID</th><th>Status</th><th>Application</th><th>User Input</th></tr>{rows}</table>"
    return layout("Runs", body)


def trace_page(run_id: str | None = None) -> str:
    rt = runtime()
    runs = rt.trace.list_runs(1)
    chosen = run_id or (runs[0]["run_id"] if runs else "")
    body = header("Trace Timeline", "Replayable step-by-step events: plan, permission, tool call, checkpoint, memory update, final answer.")
    if not chosen:
        body += "<div class='card'>No runs yet.</div>"
        return layout("Trace Timeline", body)
    events = rt.trace.get_events(chosen)
    body += f"<p>Run: <code>{html.escape(chosen)}</code></p><div class='timeline'>"
    for event in events:
        body += f"<div class='event'><strong>{html.escape(event['event_type'])}</strong> <span class='pill'>{html.escape(event.get('step_id') or 'run')}</span><pre>{html.escape(json.dumps(event.get('payload', {}), ensure_ascii=False, indent=2)[:900])}</pre></div>"
    body += "</div>"
    return layout("Trace Timeline", body)


def memory_page() -> str:
    rt = runtime()
    rows = "".join(
        f"<tr><td>#{m['id']}</td><td>{m['hit_count']}</td><td>{html.escape(m['text'][:220])}</td><td><code>{html.escape(json.dumps(m['metadata'], ensure_ascii=False)[:180])}</code></td></tr>"
        for m in rt.memory.list_memory(100)
    )
    body = header("Memory Browser", "SQLite-backed long-term memory with keyword search and hit counts.")
    body += f"<table><tr><th>ID</th><th>Hits</th><th>Text</th><th>Metadata</th></tr>{rows}</table>"
    return layout("Memory", body)


def tools_page() -> str:
    rt = runtime()
    rows = "".join(
        f"<tr><td><code>{tool['name']}</code></td><td class='{tool['risk_level']}'>{tool['risk_level']}</td><td>{'yes' if tool['enabled'] else 'no'}</td><td>{html.escape(tool['description'])}</td></tr>"
        for tool in rt.registry.list()
    )
    body = header("Tool Sandbox", "Registered BaseTool implementations with risk levels, metadata, and governance policy.")
    body += f"<table><tr><th>Tool</th><th>Risk</th><th>Enabled</th><th>Description</th></tr>{rows}</table>"
    return layout("Tools", body)


def plugins_page() -> str:
    manifest = Path("clawflow/tools/plugin_manifest.json")
    data = json.loads(manifest.read_text(encoding="utf-8")) if manifest.exists() else {"plugins": []}
    body = header("Plugin Marketplace", "Dynamic plugin tools are loaded into Tool Registry through a manifest.")
    body += f"<pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</pre>"
    return layout("Plugins", body)


def applications_page() -> str:
    apps = [
        ("Research Assistant", "Project summary, report outline, TODO", "Runtime + tools + memory + trace"),
        ("Personal Assistant", "Daily plan and long-term memory", "Memory Layer + checkpoint"),
        ("Safe Tool Call", "High-risk delete dry-run", "Permission Governance + Audit Log"),
        ("Multi-agent Project Analysis", "Role-based collaboration report", "Multi-agent + Tool Registry"),
        ("RAG Assistant", "Grounded answer from docs", "RAG + retrieval trace"),
        ("Plugin Tool Application", "Dynamic plugin execution", "Plugin Registry"),
    ]
    rows = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in apps)
    body = header("Example Applications", "These are downstream applications built on the unified ClawFlow Runtime, not isolated demo.py scripts.")
    body += f"<table><tr><th>Application</th><th>Output</th><th>Validated Infrastructure</th></tr>{rows}</table>"
    return layout("Applications", body)


def benchmark_page() -> str:
    path = Path("outputs/benchmark_results.json")
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"message": "Run clawflow benchmark first."}
    body = header("Benchmark", "Benchmark metrics generated by real AgentRuntime tasks.")
    body += f"<pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</pre>"
    for image in [
        "docs/assets/figures/benchmark_latency.png",
        "docs/assets/figures/benchmark_success_rate.png",
        "docs/assets/figures/benchmark_tool_calls.png",
        "docs/assets/figures/benchmark_trace_events.png",
    ]:
        if Path(image).exists():
            body += f"<div class='card'><img src='/{image}' style='max-width:100%'></div>"
    return layout("Benchmark", body)


def evaluation_page() -> str:
    rt = runtime()
    data = MetricsStore(rt.settings.database_path).evaluation_leaderboard()
    rows = "".join(
        f"<tr><td>{idx}</td><td>{html.escape(str(row['application']))}</td><td><code>{html.escape(str(row['run_id']))}</code></td><td>{row['score']}</td><td>{row['latency']}</td><td>{row['tool_calls']}</td><td>{row['trace_event_count']}</td></tr>"
        for idx, row in enumerate(data.get("leaderboard", []), 1)
    )
    body = header("Evaluation Leaderboard", "Application scores are computed from real benchmark outputs: success, latency, trace richness, tool calls, artifacts and governance signals.")
    if Path("docs/assets/figures/evaluation_leaderboard.png").exists():
        body += "<div class='card'><img src='/docs/assets/figures/evaluation_leaderboard.png' style='max-width:100%'></div>"
    body += f"<table><tr><th>Rank</th><th>Application</th><th>Run</th><th>Score</th><th>Latency</th><th>Tool Calls</th><th>Trace Events</th></tr>{rows}</table>"
    return layout("Evaluation", body)


def governance_page() -> str:
    rt = runtime()
    body = header("Permission Governance", "Policy Engine maps risk levels to allow/ask/deny and records every decision into Audit Log.")
    rows = "".join(
        f"""
        <tr>
          <td class='{item['risk_level']}'>{html.escape(item['risk_level'])}</td>
          <td>{html.escape(item['decision'])}</td>
          <td>{html.escape(item['source'])}</td>
          <td>{html.escape(str(item.get('reason') or ''))}</td>
        </tr>
        """
        for item in rt.policy_store.list(rt.settings.policy)
    )
    body += f"<table><tr><th>Risk</th><th>Decision</th><th>Source</th><th>Reason</th></tr>{rows}</table>"
    body += """
    <div class="card" style="margin-top:14px">
      <h3>Policy Editor</h3>
      <form method="post" action="/governance-page/policy">
        <input name="risk_level" value="high">
        <input name="decision" value="ask">
        <input name="reason" value="Keep destructive tools approval-gated for local demos.">
        <button type="submit">Save Policy</button>
      </form>
    </div>
    """
    return layout("Governance", body)


def approvals_page(message: str = "") -> str:
    rt = runtime()
    rows = "".join(
        f"""
        <tr>
          <td><code>{html.escape(item['run_id'])}</code></td>
          <td>{html.escape(item['step_id'])}</td>
          <td>{html.escape(item['tool'])}</td>
          <td class='{html.escape(item['risk_level'])}'>{html.escape(item['risk_level'])}</td>
          <td>{html.escape(item['status'])}</td>
          <td>
            <form method='post' action='/approvals-page/{html.escape(item['run_id'])}/approve' style='display:inline'><button type='submit'>Approve</button></form>
            <form method='post' action='/approvals-page/{html.escape(item['run_id'])}/deny' style='display:inline'><button type='submit' class='danger-button'>Deny</button></form>
          </td>
        </tr>
        """
        for item in rt.approvals.list(limit=100)
    )
    body = header("Human Approval", "Pending ask-level tool calls can be approved or denied from this page; decisions update SQLite, Trace, Audit Log, and run status.")
    if message:
        body += f"<div class='card'>{html.escape(message)}</div>"
    body += f"<table><tr><th>Run</th><th>Step</th><th>Tool</th><th>Risk</th><th>Status</th><th>Decision</th></tr>{rows}</table>"
    return layout("Approvals", body)


def prompts_page(rendered: str = "") -> str:
    rt = runtime()
    rows = "".join(
        f"<tr><td><code>{html.escape(item['name'])}</code></td><td>{html.escape(item['description'])}</td><td>{html.escape(item.get('tags') or '')}</td><td>{item['usage_count']}</td><td><pre>{html.escape(item['template'])}</pre></td></tr>"
        for item in rt.prompts.list()
    )
    body = header("Prompt Template Registry", "SQLite-backed prompt templates for repeatable Runtime applications.")
    body += """
    <form method="post" action="/prompts-page/render">
      <input name="name" value="research_summary">
      <textarea name="variables" rows="4">{"project":"ClawFlow"}</textarea>
      <button type="submit">Render Template</button>
    </form>
    """
    if rendered:
        body += f"<pre>{html.escape(rendered)}</pre>"
    body += f"<table><tr><th>Name</th><th>Description</th><th>Tags</th><th>Usage</th><th>Template</th></tr>{rows}</table>"
    return layout("Prompts", body)


def cost_page() -> str:
    rt = runtime()
    data = MetricsStore(rt.settings.database_path).cost_summary()
    rows = "".join(
        f"<tr><td><code>{html.escape(row['run_id'])}</code></td><td>{html.escape(str(row.get('application') or ''))}</td><td>{html.escape(row['status'])}</td><td>{row['estimated_tokens']}</td><td>{row['estimated_cost']}</td><td>{row['tool_calls']}</td><td>{row['latency']}</td></tr>"
        for row in data["runs"]
    )
    body = header("Cost Dashboard", "Local deterministic mode estimates tokens and cost from real run metrics; production providers can replace this with actual billing data.")
    body += f"<div class='grid'><div class='card'><div class='label'>Estimated Tokens</div><div class='metric'>{data['total_estimated_tokens']}</div></div><div class='card'><div class='label'>Estimated Cost</div><div class='metric'>{data['total_estimated_cost']}</div></div></div>"
    body += f"<table><tr><th>Run</th><th>Application</th><th>Status</th><th>Tokens</th><th>Cost</th><th>Tool Calls</th><th>Latency</th></tr>{rows}</table>"
    return layout("Cost", body)


def failure_page() -> str:
    rt = runtime()
    data = MetricsStore(rt.settings.database_path).failure_analysis()
    run_rows = "".join(
        f"<tr><td><code>{html.escape(row['run_id'])}</code></td><td>{html.escape(str(row.get('application') or ''))}</td><td>{html.escape(row['status'])}</td><td>{html.escape(row['user_input'][:140])}</td></tr>"
        for row in data["failed_or_pending_runs"]
    )
    event_rows = "".join(
        f"<tr><td><code>{html.escape(row['run_id'])}</code></td><td>{html.escape(row.get('step_id') or '')}</td><td><pre>{html.escape(json.dumps(row['payload'], ensure_ascii=False)[:500])}</pre></td></tr>"
        for row in data["recent_failure_events"]
    )
    body = header("Failure Analysis", "Failure, pending approval, and error signals are derived from persisted run and trace tables.")
    body += f"<h3>Runs</h3><table><tr><th>Run</th><th>Application</th><th>Status</th><th>Input</th></tr>{run_rows}</table>"
    body += f"<h3>Events</h3><table><tr><th>Run</th><th>Step</th><th>Payload</th></tr>{event_rows}</table>"
    return layout("Failures", body)


def recovery_page() -> str:
    rt = runtime()
    data = MetricsStore(rt.settings.database_path).recovery_report(rt.settings.checkpoint_dir)
    rows = "".join(
        f"<tr><td><code>{html.escape(row['run_id'])}</code></td><td>{html.escape(row['status'])}</td><td>{row['checkpoint_exists']}</td><td>{html.escape(str(row.get('approval_status')))}</td><td>{html.escape(row['recommended_action'])}</td><td><code>{html.escape(row['command'])}</code></td></tr>"
        for row in data.get("recommendations", [])
    )
    body = header("Failure Recovery Report", "Recovery guidance is derived from failed/pending runs, approval requests and checkpoint files.")
    if Path("docs/assets/figures/failure_recovery_actions.png").exists():
        body += "<div class='card'><img src='/docs/assets/figures/failure_recovery_actions.png' style='max-width:100%'></div>"
    body += f"<table><tr><th>Run</th><th>Status</th><th>Checkpoint</th><th>Approval</th><th>Action</th><th>Command</th></tr>{rows}</table>"
    return layout("Recovery", body)


def tool_usage_page() -> str:
    rt = runtime()
    data = MetricsStore(rt.settings.database_path).tool_usage()
    max_count = max([item["count"] for item in data["tools"]] or [1])
    rows = ""
    for item in data["tools"]:
        pct = int(100 * item["count"] / max_count)
        rows += f"<tr><td><code>{html.escape(item['tool'])}</code></td><td>{item['count']}</td><td><div style='height:16px;width:{pct}%;background:var(--accent);border-radius:4px'></div></td></tr>"
    body = header("Tool Usage Heatmap", "Tool usage is computed from persisted `tool_call` trace events, proving actual runtime behavior.")
    body += f"<div class='card'><div class='label'>Total Tool Calls</div><div class='metric'>{data['total_tool_calls']}</div></div>"
    body += f"<table><tr><th>Tool</th><th>Calls</th><th>Heat</th></tr>{rows}</table>"
    return layout("Tool Usage", body)


def template_generator_page(message: str = "") -> str:
    body = header("Application, Tool & Connector Template Generator", "Generate Runtime-backed application, BaseTool and MCP-like Connector scaffolds. Generated artifacts use real local persistence boundaries, not isolated demo scripts.")
    if message:
        body += f"<div class='card'>{html.escape(message)}</div>"
    body += """
    <div class="grid">
      <div class="card">
        <h3>Application Template</h3>
        <form method="post" action="/template-generator/app">
          <input name="name" value="knowledge_ops_agent">
          <textarea name="task" rows="4">请基于 ClawFlow Runtime 构建知识运营助手。</textarea>
          <button type="submit">Generate Application</button>
        </form>
      </div>
      <div class="card">
        <h3>Tool Template</h3>
        <form method="post" action="/template-generator/tool">
          <input name="name" value="local_crm_lookup">
          <input name="risk" value="medium">
          <button type="submit">Generate Tool</button>
        </form>
      </div>
      <div class="card">
        <h3>Connector Template</h3>
        <form method="post" action="/template-generator/connector">
          <input name="name" value="enterprise_ticket_connector">
          <input name="operation" value="sync_ticket">
          <button type="submit">Generate Connector</button>
        </form>
      </div>
    </div>
    """
    generated = sorted(Path("applications").glob("generated_*"), key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
    generated_tools = sorted(Path("clawflow/tools/generated").glob("*_tool.py")) if Path("clawflow/tools/generated").exists() else []
    generated_connectors = sorted(Path("clawflow/connectors/generated").glob("*.py")) if Path("clawflow/connectors/generated").exists() else []
    body += "<h3>Generated Artifacts</h3><table><tr><th>Type</th><th>Path</th></tr>"
    for path in generated[:20]:
        body += f"<tr><td>Application</td><td><code>{html.escape(str(path))}</code></td></tr>"
    for path in generated_tools[:20]:
        body += f"<tr><td>Tool</td><td><code>{html.escape(str(path))}</code></td></tr>"
    for path in generated_connectors[:20]:
        if path.name != "__init__.py":
            body += f"<tr><td>Connector</td><td><code>{html.escape(str(path))}</code></td></tr>"
    body += "</table>"
    return layout("Templates", body)


def audit_page() -> str:
    rt = runtime()
    rows = "".join(
        f"<tr><td>{event['id']}</td><td><code>{html.escape(event.get('run_id') or '')}</code></td><td>{html.escape(event.get('tool') or '')}</td><td class='{event.get('risk_level')}'>{html.escape(event.get('risk_level') or '')}</td><td>{html.escape(event.get('decision') or '')}</td><td>{html.escape(event.get('reason') or '')}</td></tr>"
        for event in rt.audit.list_events(100)
    )
    body = header("Audit Log", "Every permission decision is persisted for accountability and replay.")
    body += f"<table><tr><th>ID</th><th>Run</th><th>Tool</th><th>Risk</th><th>Decision</th><th>Reason</th></tr>{rows}</table>"
    return layout("Audit Log", body)


def workflow_page() -> str:
    files = sorted(Path("outputs").glob("workflow_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    data = json.loads(files[0].read_text(encoding="utf-8")) if files else {"message": "Run an application to generate workflow graph JSON."}
    body = header("Workflow Graph", "DAG-style step graph exported from the latest runtime plan.")
    body += f"<pre>{html.escape(json.dumps(data, ensure_ascii=False, indent=2))}</pre>"
    return layout("Workflow Graph", body)


def multi_agent_page() -> str:
    path = Path("outputs/multi_agent_report.md")
    text = path.read_text(encoding="utf-8") if path.exists() else "Run `clawflow app multi-agent` first."
    body = header("Multi-agent Collaboration", "ManagerAgent, ResearchAgent, ToolAgent, CriticAgent, MemoryAgent, ReportAgent, SlideAgent, GovernanceAgent.")
    body += f"<pre>{html.escape(text[:5000])}</pre>"
    return layout("Multi-agent", body)


def rag_page() -> str:
    path = Path("outputs/rag_answer.md")
    text = path.read_text(encoding="utf-8") if path.exists() else "Run `clawflow app rag` first."
    body = header("RAG Assistant", "Document loader, chunker, keyword retriever, vector-store interface placeholder, retrieval trace.")
    body += f"<pre>{html.escape(text[:5000])}</pre>"
    return layout("RAG", body)


def roadmap_page() -> str:
    text = Path("ROADMAP.md").read_text(encoding="utf-8") if Path("ROADMAP.md").exists() else "Roadmap will be generated."
    body = header("Roadmap", "From local prototype to deployable AgentOS infrastructure.")
    body += f"<pre>{html.escape(text)}</pre>"
    return layout("Roadmap", body)
