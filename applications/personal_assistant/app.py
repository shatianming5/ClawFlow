from clawflow.core.runtime import AgentRuntime


TASK = "请帮我制定明天的学习计划，并保存为 daily_plan.md，同时写入长期记忆。"


def main():
    return AgentRuntime().run(TASK, application="personal_assistant", auto_approve=True)


if __name__ == "__main__":
    print(main().final_answer)

