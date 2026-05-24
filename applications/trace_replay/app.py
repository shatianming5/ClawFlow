from clawflow.core.runtime import AgentRuntime


def main():
    runtime = AgentRuntime()
    result = runtime.run("请分析当前项目结构，生成可回放 trace。", application="trace_replay", auto_approve=True)
    replay = runtime.replay(result.run_id)
    path = runtime.settings.root_dir / "outputs" / "trace_replay.txt"
    path.write_text(replay, encoding="utf-8")
    return result


if __name__ == "__main__":
    print(main().final_answer)

