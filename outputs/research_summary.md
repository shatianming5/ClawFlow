# Research Summary

ClawFlow is structured as a lightweight Agent Runtime / AgentOS infrastructure prototype.
The current workspace contains 500 sampled files across clawflow, applications, docs, scripts, tests.

## File type distribution
- `.json`: 382
- `.md`: 47
- `.py`: 41
- `.txt`: 6
- `.png`: 5
- `[no_ext]`: 4
- `.pdf`: 2
- `.docx`: 1
- `.example`: 1
- `.jsonl`: 1
- `.log`: 1
- `.pid`: 1

## README signal
# ClawFlow

**A Lightweight Agent Runtime for Next-Generation Personal AI Agents**

> 让智能体从能回答走向能执行、能记忆、能恢复、能协作、能治理。

ClawFlow is a lightweight **Agent Runtime / AgentOS Kernel** prototype for building next-generation personal AI agents. It is not a ChatGPT API wrapper and not a folder of isolated demo scripts. It provides a reusable infrastructure layer for **Workflow Orchestration**, **Checkpoint & Resume**, **Tool Sandbox**, **Permission Governance**, **Memory Layer**, **Observability**, **Trace Replay**, **Plugin Registry**, **MCP-like Connector**, **RAG Module**, **Event Bus**, **Scheduler**, **Benchmark & Evaluation**, and **Multi-agent Collaboration**.

![Architecture](docs/assets/diagrams/architecture.png)

## Why ClawFlow is not just demos

- Example Applications are validation workloads for the framework, not the project body.
- Every application goes through the same `AgentRuntime`, Planner, Executor, Tool Registry, Memory Layer, Trace Store, Checkpoint Store and Permission Governance path.
- Developers can use these applications as templates to build their own agent applications.
- ClawFlow's core is **Agent Runtime / AgentOS Infrastructure**.
- The implementation uses 

## Framework capability mapping
- Runtime: planner, executor, tool calling, checkpoint, resume.
- Governance: risk-level policy, approval events, audit log.
- Observability: run table, structured trace events, replay export.
- Applications: downstream tasks must use the unified Runtime instead of isolated demo scripts.
