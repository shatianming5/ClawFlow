from clawflow.core.runtime import AgentRuntime


TASK = "请根据 docs 中的项目文档回答 ClawFlow 的核心创新点。"


def main():
    return AgentRuntime().run(TASK, application="rag_assistant", auto_approve=True)


if __name__ == "__main__":
    print(main().final_answer)

