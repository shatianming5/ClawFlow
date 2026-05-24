from clawflow.core.runtime import AgentRuntime


TASK = "请分析当前项目结构，生成项目摘要、README 摘要、技术报告大纲和 TODO 列表。"


def main():
    return AgentRuntime().run(TASK, application="research_assistant", auto_approve=True)


if __name__ == "__main__":
    result = main()
    print(result.final_answer)

