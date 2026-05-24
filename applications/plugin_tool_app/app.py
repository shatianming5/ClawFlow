from clawflow.core.runtime import AgentRuntime


TASK = "请运行插件工具并展示插件注册能力。"


def main():
    return AgentRuntime().run(TASK, application="plugin_tool_app", auto_approve=True)


if __name__ == "__main__":
    print(main().final_answer)

