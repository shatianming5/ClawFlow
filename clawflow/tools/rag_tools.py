from __future__ import annotations

from clawflow.core.schema import ToolResult
from clawflow.rag.rag_engine import RagEngine
from clawflow.tools.base import BaseTool, ToolContext


class SearchKnowledgeBaseTool(BaseTool):
    name = "search_knowledge_base"
    description = "Search persisted memory and local project docs as a lightweight knowledge base."
    risk_level = "low"

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        query = str(args.get("query", context.user_input))
        memories = context.memory.search_memory(query, limit=int(args.get("limit", 5)))
        engine = RagEngine(context.settings.root_dir)
        docs = engine.retrieve(query, limit=int(args.get("limit", 5)))
        return ToolResult(ok=True, data={"query": query, "memories": memories, "documents": docs})


class RagAnswerTool(BaseTool):
    name = "rag_answer"
    description = "Generate a local RAG answer from retrieved project documentation chunks."
    risk_level = "low"

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        query = str(args.get("query", context.user_input))
        engine = RagEngine(context.settings.root_dir)
        answer = engine.answer(query)
        output_path = context.settings.root_dir / args.get("path", "outputs/rag_answer.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(answer["markdown"], encoding="utf-8")
        if context.trace:
            context.trace.record(context.run_id, "retrieval", {"query": query, "chunks": answer["chunks"]}, context.step_id)
        context.memory.add_memory(
            f"RAG answer generated for query: {query}",
            {"type": "rag_answer", "path": str(output_path), "run_id": context.run_id},
        )
        return ToolResult(ok=True, data=answer, artifacts=[str(output_path)])

