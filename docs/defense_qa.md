# ClawFlow Defense Q&A

## What is ClawFlow?

ClawFlow is a lightweight Agent Runtime / AgentOS Kernel prototype. It turns agent execution into a governed, observable and recoverable lifecycle rather than a one-shot prompt response.

## Why is it not just a ChatGPT wrapper?

The local mode runs without an external LLM key. Planning is performed by `DeterministicLocalProvider`, tools are called through `ToolRegistry`, state is persisted in SQLite/JSONL/files, and every run records trace, checkpoint, audit and memory events.

## Why are the applications not demos?

Each application calls the same `AgentRuntime`; none of the core examples bypass Planner, Executor, Tool Registry, Governance, Memory, Trace or Checkpoint. The applications validate infrastructure capability and serve as developer templates.

## What are the main innovations?

- AgentOS Kernel abstraction for task lifecycle management.
- Checkpoint & Resume for interrupted or approval-gated runs.
- Tool Sandbox and Permission Governance with audit log.
- Trace Replay and runtime observability dashboard.
- Memory Layer with persistent search and hit counts.
- Plugin Registry and MCP-like connector boundary.
- RAG and Multi-agent Collaboration through the unified Runtime.
- Benchmark, Evaluation Leaderboard and Failure Recovery Report.

## How does ClawFlow handle risky tools?

Tools declare `risk_level`. The Policy Engine maps risk to allow/ask/deny. High-risk delete requests use `delete_file_dry_run`, create an audit record and can pause at Human Approval.

## What can be replaced in production?

SQLite can be replaced by a server database, JSONL trace by a trace backend, keyword retrieval by a vector database, local email/calendar by real SaaS connectors, and deterministic planning by an OpenAI-compatible provider.

## What should be shown during the demo?

1. Run `clawflow app research`.
2. Show `clawflow trace list` and `clawflow trace replay <run_id>`.
3. Open `/dashboard`, `/trace-timeline`, `/memory-browser`, `/governance-page`, `/approvals-page`, `/benchmark-page`, `/evaluation-leaderboard`, `/failure-recovery`.
4. Show `outputs/benchmark_results.md` and `outputs/evaluation_leaderboard.md`.
5. Show the PPT architecture and screenshots.

## What are the current limitations?

This is a lightweight local prototype for course/challenge validation. It is not a production-scale distributed system yet. Production deployment would need stronger auth, distributed queues, real connector credentials, vector databases, cloud trace storage and stronger policy administration.

