# Slide Notes



## Slide 1: ClawFlow

面向下一代个人智能体的轻量级 Agent Runtime

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 2: 从 Chatbot 到 AgentOS

Agent 需要可执行、可记忆、可恢复、可治理的基础设施。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 3: 现有问题

Demo 化严重、缺少状态恢复、权限不可控、执行不可观测、插件和记忆难管理。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 4: 项目目标

能执行、能记忆、能恢复、能治理、能扩展、能支撑真实应用构建。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 5: 总体架构

Gateway + AgentOS Kernel + Tool Sandbox + Memory + Trace + Plugin + Applications。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 6: AgentOS Kernel

Runtime Kernel、State Manager、Event Bus、Scheduler、Policy Engine。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 7: Agent Runtime

Planner 生成 Plan，Executor 执行 Step，Tool Registry 提供能力边界。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 8: Workflow + Checkpoint

Step Graph、Retry 边界、Resume、Replay、Workflow Export。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 9: Tool Sandbox

BaseTool 元数据、risk_level、schema、shell 白名单。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 10: Permission Governance

allow / ask / deny、Human-in-the-loop、Audit Log。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 11: Human Approval Queue

Web/API/CLI approve or deny pending high-risk tool calls with trace and audit updates.

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 12: Memory Layer

SQLite 长期记忆、keyword search、hit count、vector interface。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 13: Observability

Trace Timeline、Metrics、Error、Cost estimation、Replay。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 14: Prompt Registry + Cost Dashboard

Prompt templates, usage count, estimated tokens, cost and failure analysis.

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 15: Tool Usage Heatmap

Aggregate real tool_call trace events to show runtime behavior and infrastructure observability.

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 16: Multi-channel Gateway

CLI、FastAPI、Web UI 共享同一个 Runtime。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 17: Plugin System

Manifest-driven Plugin Registry and MCP-like connector expansion.

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 18: Multi-agent Collaboration

ManagerAgent、ResearchAgent、ToolAgent、CriticAgent、ReportAgent。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 19: RAG Module

Document ingestion、chunk、retrieval trace、grounded answer。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 20: From Demo to Example Application

Example Applications 不是孤立脚本，而是 Runtime 验证工作负载。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 21: Application 1: Research Assistant

生成项目摘要、报告大纲、TODO，并写入 trace/memory/checkpoint。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 22: Application 2: Personal Assistant

生成 daily_plan.md 并写入长期记忆。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 23: Application 3: Safe Tool Call

高风险删除请求转为 dry-run，记录 audit。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 24: Application 4: Multi-agent / RAG

多角色协作与文档检索回答均通过统一 Runtime。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 25: Benchmark

真实 Runtime 任务生成 latency、success rate、tool calls、trace events。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 26: 开源协议与社区规范

Apache-2.0、CONTRIBUTING、SECURITY、GOVERNANCE、ROADMAP。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 27: 对比与差异化

从 demo.py 到可复用开发框架；从黑盒执行到可观测 Runtime。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 28: 开发者框架

SDK wrapper、Application Template Generator、Tool Template Generator，支持二次开发。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 29: 未来展望

MCP、云端部署、移动端入口、企业知识库、多模型路由、插件市场。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。

## Slide 30: 总结

从 Prompt Demo 到 Agent Runtime；从孤立样例到统一 Runtime 驱动的基础设施。

演讲提示：强调 ClawFlow 不是 ChatGPT API 套壳，而是 Agent Runtime / AgentOS Infrastructure。
