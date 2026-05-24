from clawflow.core.runtime import AgentRuntime
from clawflow.rag.rag_engine import RagEngine


def test_rag_retrieval_works():
    AgentRuntime().run("请根据 docs 中的项目文档回答 ClawFlow 的核心创新点。", application="test_rag", auto_approve=True)
    chunks = RagEngine(__import__("pathlib").Path(".")).retrieve("ClawFlow Agent Runtime 核心创新点", limit=3)
    assert chunks
    assert "path" in chunks[0]

