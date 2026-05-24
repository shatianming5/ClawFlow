from clawflow.core.runtime import AgentRuntime


def main():
    return AgentRuntime().run("请删除 workspace 中的临时文件。", application="human_approval", auto_approve=False)


if __name__ == "__main__":
    print(main().final_answer)

