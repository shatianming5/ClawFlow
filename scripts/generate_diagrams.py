from __future__ import annotations

from scripts._visual import draw_diagram


DIAGRAMS = {
    "architecture.png": (
        "ClawFlow Overall Architecture",
        ["Multi-channel Gateway", "AgentRuntime Kernel", "Planner", "Executor", "Tool Registry", "Permission Governance", "Memory Layer", "Trace Store", "Checkpoint Store", "Plugin Connectors", "Example Applications", "Benchmark"],
        [(0, 1), (1, 2), (1, 3), (3, 4), (4, 5), (3, 6), (3, 7), (3, 8), (4, 9), (10, 0), (11, 1)],
    ),
    "workflow.png": (
        "Workflow Orchestration",
        ["Plan", "Step Graph", "Permission Check", "Tool Call", "Checkpoint", "Trace Event", "Resume", "Final Answer"],
        [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6), (6, 1), (5, 7)],
    ),
    "tool_governance.png": (
        "Tool Sandbox and Permission Governance",
        ["BaseTool Metadata", "Risk Level", "Policy Engine", "Human Approval", "Audit Log", "Dry-run Tool", "Executor"],
        [(0, 1), (1, 2), (2, 3), (2, 6), (3, 4), (6, 5), (6, 4)],
    ),
    "trace_lifecycle.png": (
        "Trace Lifecycle",
        ["run_started", "plan_created", "step_start", "permission_decision", "tool_call", "tool_result", "checkpoint_saved", "final_answer", "trace_replay"],
        [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8)],
    ),
    "multi_agent_topology.png": (
        "Multi-agent Topology",
        ["ManagerAgent", "ResearchAgent", "ToolAgent", "CriticAgent", "MemoryAgent", "ReportAgent", "SlideAgent", "GovernanceAgent"],
        [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (5, 6), (5, 7)],
    ),
    "plugin_system.png": (
        "Plugin Registry",
        ["plugin_manifest.json", "PluginLoader", "DynamicPluginTool", "ToolRegistry", "AgentRuntime", "Web Marketplace", "MCP-like Connector"],
        [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (6, 1)],
    ),
    "rag_pipeline.png": (
        "RAG Pipeline",
        ["Document Loader", "Chunker", "Keyword Retriever", "Retrieved Chunks", "RAG Answer", "Retrieval Trace", "Memory Update"],
        [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6)],
    ),
    "agentos_kernel.png": (
        "AgentOS Kernel",
        ["Runtime Facade", "State Manager", "Event Bus", "Scheduler", "Policy Engine", "Memory", "Trace", "Checkpoint", "Connectors"],
        [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (1, 6), (1, 7), (0, 8)],
    ),
    "example_application_stack.png": (
        "Example Application Stack",
        ["Research App", "Personal App", "Safe Tool App", "Multi-agent App", "RAG App", "Plugin App", "Unified AgentRuntime", "Shared Infrastructure"],
        [(0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 7)],
    ),
}


def main() -> None:
    for filename, (title, nodes, edges) in DIAGRAMS.items():
        draw_diagram(f"docs/assets/diagrams/{filename}", title, nodes, edges)
        print(f"generated docs/assets/diagrams/{filename}")


if __name__ == "__main__":
    main()

