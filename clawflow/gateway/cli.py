from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from clawflow.config.settings import load_settings
from clawflow.core.runtime import AgentRuntime


APP_TASKS = {
    "research": ("请分析当前项目结构，生成项目摘要、README 摘要、技术报告大纲和 TODO 列表。", True),
    "personal": ("请帮我制定明天的学习计划，并保存为 daily_plan.md，同时写入长期记忆。", True),
    "safe": ("请删除 workspace 中的临时文件。", True),
    "multi-agent": ("请让多个智能体协作完成一次项目分析。", True),
    "rag": ("请根据 docs 中的项目文档回答 ClawFlow 的核心创新点。", True),
    "plugin": ("请运行插件工具并展示插件注册能力。", True),
    "trace-replay": ("请分析当前项目结构，生成可回放 trace。", True),
    "human-approval": ("请删除 workspace 中的临时文件。", False),
    "benchmark": ("请汇总 benchmark 结果。", True),
    "web": ("请生成 Web Dashboard 展示数据。", True),
}


def _runtime() -> AgentRuntime:
    return AgentRuntime(load_settings())


def _print_result(result) -> None:
    print(f"run_id: {result.run_id}")
    print(f"status: {result.status}")
    print(result.final_answer)


def run_cmd(args: argparse.Namespace) -> None:
    result = _runtime().run(args.task, application="cli", auto_approve=args.yes, interactive=args.interactive)
    _print_result(result)


def app_cmd(args: argparse.Namespace) -> None:
    if args.name == "benchmark":
        from scripts.run_benchmark import main as benchmark_main

        benchmark_main()
    task, default_approve = APP_TASKS[args.name]
    result = _runtime().run(task, application=args.name, auto_approve=args.yes or default_approve, interactive=args.interactive)
    _print_result(result)
    if args.name == "trace-replay":
        print(_runtime().replay(result.run_id))


def resume_cmd(args: argparse.Namespace) -> None:
    result = _runtime().resume(args.run_id, auto_approve=args.yes, interactive=args.interactive)
    _print_result(result)


def trace_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        for run in runtime.trace.list_runs(limit=args.limit):
            print(f"{run['run_id']} {run['status']} {run.get('application') or ''} {run['user_input'][:80]}")
    elif args.action == "show":
        events = runtime.trace.get_events(args.run_id)
        print(json.dumps(events, ensure_ascii=False, indent=2))
    elif args.action == "export":
        path = runtime.export_trace(args.run_id)
        print(path)
    elif args.action == "replay":
        print(runtime.replay(args.run_id))


def memory_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        for mem in runtime.memory.list_memory(limit=args.limit):
            print(f"#{mem['id']} hits={mem['hit_count']} {mem['text'][:120]}")
    elif args.action == "add":
        print(runtime.memory.add_memory(args.text, {"source": "cli"}))
    elif args.action == "search":
        print(json.dumps(runtime.memory.search_memory(args.query), ensure_ascii=False, indent=2))


def tools_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        for tool in runtime.registry.list():
            status = "enabled" if tool["enabled"] else "disabled"
            print(f"{tool['name']} [{tool['risk_level']}] {status} - {tool['description']}")


def approvals_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        for item in runtime.approvals.list(status=args.status):
            print(f"{item['run_id']} {item['step_id']} {item['tool']} risk={item['risk_level']} status={item['status']}")
    elif args.action == "approve":
        _print_result(runtime.approve(args.run_id))
    elif args.action == "deny":
        _print_result(runtime.deny(args.run_id))


def prompts_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        for item in runtime.prompts.list():
            print(f"{item['name']} usage={item['usage_count']} tags={item.get('tags') or ''} - {item['description']}")
    elif args.action == "add":
        print(runtime.prompts.upsert(args.name, args.template, args.description or "", args.tags or ""))
    elif args.action == "render":
        variables = json.loads(args.variables or "{}")
        print(runtime.prompts.render(args.name, variables))


def metrics_cmd(args: argparse.Namespace) -> None:
    from clawflow.observability.metrics import MetricsStore

    runtime = _runtime()
    store = MetricsStore(runtime.settings.database_path)
    if args.kind == "summary":
        print(json.dumps(store.summary(), ensure_ascii=False, indent=2))
    elif args.kind == "cost":
        print(json.dumps(store.cost_summary(), ensure_ascii=False, indent=2))
    elif args.kind == "failures":
        print(json.dumps(store.failure_analysis(), ensure_ascii=False, indent=2))
    elif args.kind == "tools":
        print(json.dumps(store.tool_usage(), ensure_ascii=False, indent=2))


def policy_cmd(args: argparse.Namespace) -> None:
    runtime = _runtime()
    if args.action == "list":
        print(json.dumps(runtime.policy_store.list(runtime.settings.policy), ensure_ascii=False, indent=2))
    elif args.action == "set":
        runtime.policy_store.set_decision(args.risk_level, args.decision, args.reason or "")
        print(json.dumps(runtime.policy_store.get_policy(runtime.settings.policy), ensure_ascii=False, indent=2))


def benchmark_cmd(args: argparse.Namespace) -> None:
    from scripts.run_benchmark import main as benchmark_main

    benchmark_main()


def generate_cmd(args: argparse.Namespace) -> None:
    if args.kind == "app":
        from scripts.create_application_template import create_application

        print(create_application(args.name, args.task or "请基于 ClawFlow Runtime 执行一个可观测任务。"))
    elif args.kind == "tool":
        from scripts.create_tool_template import create_tool

        print(create_tool(args.name, args.risk))


def serve_cmd(args: argparse.Namespace) -> None:
    settings = load_settings()
    host = args.host or settings.web_host
    port = args.port or settings.web_port
    try:
        import uvicorn
    except ImportError:
        print("uvicorn is not installed. Run `make install` first.", file=sys.stderr)
        raise SystemExit(2)
    uvicorn.run("clawflow.gateway.api:app", host=host, port=port, reload=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="clawflow", description="ClawFlow Agent Runtime CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run")
    run.add_argument("task")
    run.add_argument("--yes", action="store_true", help="auto-approve ask-level local operations")
    run.add_argument("--interactive", action="store_true")
    run.set_defaults(func=run_cmd)

    serve = sub.add_parser("serve")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    serve.set_defaults(func=serve_cmd)

    resume = sub.add_parser("resume")
    resume.add_argument("run_id")
    resume.add_argument("--yes", action="store_true")
    resume.add_argument("--interactive", action="store_true")
    resume.set_defaults(func=resume_cmd)

    trace = sub.add_parser("trace")
    trace.add_argument("action", choices=["list", "show", "export", "replay"])
    trace.add_argument("run_id", nargs="?")
    trace.add_argument("--limit", type=int, default=20)
    trace.set_defaults(func=trace_cmd)

    memory = sub.add_parser("memory")
    memory.add_argument("action", choices=["list", "add", "search"])
    memory.add_argument("text", nargs="?")
    memory.add_argument("--query")
    memory.add_argument("--limit", type=int, default=20)
    memory.set_defaults(func=memory_cmd)

    tools = sub.add_parser("tools")
    tools.add_argument("action", choices=["list"])
    tools.set_defaults(func=tools_cmd)

    approvals = sub.add_parser("approvals")
    approvals.add_argument("action", choices=["list", "approve", "deny"])
    approvals.add_argument("run_id", nargs="?")
    approvals.add_argument("--status")
    approvals.set_defaults(func=approvals_cmd)

    prompts = sub.add_parser("prompts")
    prompts.add_argument("action", choices=["list", "add", "render"])
    prompts.add_argument("name", nargs="?")
    prompts.add_argument("--template")
    prompts.add_argument("--description")
    prompts.add_argument("--tags")
    prompts.add_argument("--variables")
    prompts.set_defaults(func=prompts_cmd)

    metrics = sub.add_parser("metrics")
    metrics.add_argument("kind", choices=["summary", "cost", "failures", "tools"], default="summary", nargs="?")
    metrics.set_defaults(func=metrics_cmd)

    policy = sub.add_parser("policy")
    policy.add_argument("action", choices=["list", "set"])
    policy.add_argument("risk_level", nargs="?")
    policy.add_argument("decision", nargs="?")
    policy.add_argument("--reason")
    policy.set_defaults(func=policy_cmd)

    app = sub.add_parser("app")
    app.add_argument("name", choices=sorted(APP_TASKS))
    app.add_argument("--yes", action="store_true")
    app.add_argument("--interactive", action="store_true")
    app.set_defaults(func=app_cmd)

    bench = sub.add_parser("benchmark")
    bench.set_defaults(func=benchmark_cmd)

    generate = sub.add_parser("generate")
    generate.add_argument("kind", choices=["app", "tool"])
    generate.add_argument("name")
    generate.add_argument("--task")
    generate.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    generate.set_defaults(func=generate_cmd)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
