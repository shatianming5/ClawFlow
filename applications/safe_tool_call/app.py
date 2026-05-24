from clawflow.core.runtime import AgentRuntime


TASK = "请删除 workspace 中的临时文件。"


def main():
    return AgentRuntime().run(TASK, application="safe_tool_call", auto_approve=True)


if __name__ == "__main__":
    print(main().final_answer)

