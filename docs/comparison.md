# ClawFlow Comparison and Positioning

ClawFlow is positioned as a lightweight local Agent Runtime / AgentOS infrastructure prototype. It does not try to replace mature agent frameworks; it packages the core engineering concerns needed for a course/challenge deliverable and GitHub-ready project.

| Dimension | ClawFlow | Graph/state frameworks | Multi-agent frameworks | Provider SDK stacks | Ordinary demo.py projects |
|---|---|---|---|---|---|
| Primary focus | Lightweight AgentOS runtime and infrastructure packaging | Graph/state orchestration | Multi-agent conversation workflows | Provider-backed agents, tools and handoff | One-off demonstration |
| Local no-key mode | Yes, deterministic local planner | Depends on implementation | Depends on implementation | Usually provider-centric | Often no |
| Persistent trace | Built in with SQLite + JSONL | Often configurable | Often external | Provider/tooling dependent | Rare |
| Checkpoint & resume | Built in | Core in graph systems | Not always central | Depends on app design | Rare |
| Permission governance | Built in with risk policy and audit | App-specific | App-specific | Guardrails/tool policies possible | Rare |
| Web dashboard | Included | Usually external | Usually external | Usually external | Rare |
| Report/PPT/screenshots | Generated as project deliverables | Not a framework goal | Not a framework goal | Not a framework goal | Rare |
| Target use | Teaching, research, challenge, prototype infrastructure | Production-grade orchestration | Agent collaboration experiments | Provider-integrated app development | Quick proof of concept |

## Differentiation

ClawFlow's strength is not raw model intelligence. Its strength is infrastructure completeness: CLI, API, Web Dashboard, Memory, Trace, Checkpoint, Governance, RAG, Plugin Registry, Multi-agent Collaboration, Benchmark, Evaluation, Recovery, Report, PPT and Open-source Community files in one runnable package.

## Honest Boundary

ClawFlow is a prototype and local validation system. The design reserves replacement interfaces for production backends, but it should not be described as a mature industrial-scale platform.

