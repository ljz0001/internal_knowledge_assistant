try:
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    from langgraph.checkpoint.memory import InMemorySaver as MemorySaver

_memory_saver = None

def get_memory_saver():
    global _memory_saver

    if _memory_saver is None:
        _memory_saver = MemorySaver()
    return _memory_saver
