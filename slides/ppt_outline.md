# ClawFlow PPT Outline

1. ClawFlow - 面向下一代个人智能体的轻量级 Agent Runtime
   - Asset: `docs/assets/diagrams/architecture.png`
2. 从 Chatbot 到 AgentOS - Agent 需要可执行、可记忆、可恢复、可治理的基础设施。
   - Asset: `docs/assets/diagrams/agentos_kernel.png`
3. 现有问题 - Demo 化严重、缺少状态恢复、权限不可控、执行不可观测、插件和记忆难管理。
4. 项目目标 - 能执行、能记忆、能恢复、能治理、能扩展、能支撑真实应用构建。
5. 总体架构 - Gateway + AgentOS Kernel + Tool Sandbox + Memory + Trace + Plugin + Applications。
   - Asset: `docs/assets/diagrams/architecture.png`
6. AgentOS Kernel - Runtime Kernel、State Manager、Event Bus、Scheduler、Policy Engine。
   - Asset: `docs/assets/diagrams/agentos_kernel.png`
7. Agent Runtime - Planner 生成 Plan，Executor 执行 Step，Tool Registry 提供能力边界。
   - Asset: `docs/assets/diagrams/workflow.png`
8. Workflow + Checkpoint - Step Graph、Retry 边界、Resume、Replay、Workflow Export。
   - Asset: `docs/assets/diagrams/workflow.png`
9. Tool Sandbox - BaseTool 元数据、risk_level、schema、shell 白名单。
   - Asset: `docs/assets/diagrams/tool_governance.png`
10. Permission Governance - allow / ask / deny、Human-in-the-loop、Audit Log。
   - Asset: `docs/assets/screenshots/web_governance.png`
11. Human Approval Queue - Web/API/CLI approve or deny pending high-risk tool calls with trace and audit updates.
   - Asset: `docs/assets/screenshots/web_approvals.png`
12. Memory Layer - SQLite 长期记忆、keyword search、hit count、vector interface。
   - Asset: `docs/assets/screenshots/web_memory.png`
13. Observability - Trace Timeline、Metrics、Error、Cost estimation、Replay。
   - Asset: `docs/assets/screenshots/web_trace_timeline.png`
14. Prompt Registry + Cost Dashboard - Prompt templates, usage count, estimated tokens, cost and failure analysis.
   - Asset: `docs/assets/screenshots/web_cost_dashboard.png`
15. Tool Usage Heatmap - Aggregate real tool_call trace events to show runtime behavior and infrastructure observability.
   - Asset: `docs/assets/screenshots/web_tool_usage_heatmap.png`
16. Multi-channel Gateway - CLI、FastAPI、Web UI 共享同一个 Runtime。
   - Asset: `docs/assets/screenshots/web_home.png`
17. Plugin System - Manifest-driven Plugin Registry and MCP-like connector expansion.
   - Asset: `docs/assets/diagrams/plugin_system.png`
18. Multi-agent Collaboration - ManagerAgent、ResearchAgent、ToolAgent、CriticAgent、ReportAgent。
   - Asset: `docs/assets/diagrams/multi_agent_topology.png`
19. RAG Module - Document ingestion、chunk、retrieval trace、grounded answer。
   - Asset: `docs/assets/diagrams/rag_pipeline.png`
20. From Demo to Example Application - Example Applications 不是孤立脚本，而是 Runtime 验证工作负载。
   - Asset: `docs/assets/diagrams/example_application_stack.png`
21. Application 1: Research Assistant - 生成项目摘要、报告大纲、TODO，并写入 trace/memory/checkpoint。
   - Asset: `docs/assets/screenshots/cli_research_application.png`
22. Application 2: Personal Assistant - 生成 daily_plan.md 并写入长期记忆。
   - Asset: `docs/assets/screenshots/web_memory.png`
23. Application 3: Safe Tool Call - 高风险删除请求转为 dry-run，记录 audit。
   - Asset: `docs/assets/screenshots/web_audit_log.png`
24. Application 4: Multi-agent / RAG - 多角色协作与文档检索回答均通过统一 Runtime。
   - Asset: `docs/assets/screenshots/web_multi_agent.png`
25. Benchmark - 真实 Runtime 任务生成 latency、success rate、tool calls、trace events。
   - Asset: `docs/assets/figures/benchmark_latency.png`
26. 开源协议与社区规范 - Apache-2.0、CONTRIBUTING、SECURITY、GOVERNANCE、ROADMAP。
27. 对比与差异化 - 从 demo.py 到可复用开发框架；从黑盒执行到可观测 Runtime。
28. 开发者框架 - SDK wrapper、Application Template Generator、Tool Template Generator，支持二次开发。
   - Asset: `docs/assets/screenshots/web_applications.png`
29. 未来展望 - MCP、云端部署、移动端入口、企业知识库、多模型路由、插件市场。
   - Asset: `docs/assets/screenshots/web_applications.png`
30. 总结 - 从 Prompt Demo 到 Agent Runtime；从孤立样例到统一 Runtime 驱动的基础设施。
   - Asset: `docs/assets/screenshots/web_benchmark.png`
