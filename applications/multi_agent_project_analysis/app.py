from clawflow.core.runtime import AgentRuntime


TASK = "请让多个智能体协作完成一次项目分析。"


def main():
    return AgentRuntime().run(TASK, application="multi_agent_project_analysis", auto_approve=True)


if __name__ == "__main__":
    print(main().final_answer)

