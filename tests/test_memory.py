from clawflow.config.settings import load_settings
from clawflow.memory.memory_store import MemoryStore


def test_memory_add_search_list_delete_works():
    memory = MemoryStore(load_settings().database_path)
    memory_id = memory.add_memory("ClawFlow memory test entry", {"type": "test"})
    hits = memory.search_memory("ClawFlow memory")
    assert any(hit["id"] == memory_id for hit in hits)
    assert any(mem["id"] == memory_id for mem in memory.list_memory())
    assert memory.delete_memory(memory_id)

