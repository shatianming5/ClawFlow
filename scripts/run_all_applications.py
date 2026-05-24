from __future__ import annotations

from pathlib import Path

from clawflow.core.runtime import AgentRuntime


APPLICATIONS = [
    ("research_assistant", "请分析当前项目结构，生成项目摘要、README 摘要、技术报告大纲和 TODO 列表。", True),
    ("personal_assistant", "请帮我制定明天的学习计划，并保存为 daily_plan.md，同时写入长期记忆。", True),
    ("safe_tool_call", "请删除 workspace 中的临时文件。", True),
    ("multi_agent_project_analysis", "请让多个智能体协作完成一次项目分析。", True),
    ("rag_assistant", "请根据 docs 中的项目文档回答 ClawFlow 的核心创新点。", True),
    ("plugin_tool_app", "请运行插件工具并展示插件注册能力。", True),
    ("human_approval", "请删除 workspace 中的临时文件。", False),
]


def main() -> list[dict]:
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/sample.temp").write_text("temporary file for dry-run governance demo\n", encoding="utf-8")
    runtime = AgentRuntime()
    rows = []
    for name, task, approve in APPLICATIONS:
        result = runtime.run(task, application=name, auto_approve=approve)
        rows.append({"application": name, "run_id": result.run_id, "status": result.status, "artifacts": result.artifacts})
    lines = ["# Application Run Summary", ""]
    for row in rows:
        lines.append(f"- {row['application']}: `{row['run_id']}` status={row['status']} artifacts={len(row['artifacts'])}")
    Path("outputs/run_all_applications.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


if __name__ == "__main__":
    for item in main():
        print(f"{item['application']} {item['run_id']} {item['status']}")

