from langgraph.checkpoint.memory import MemorySaver
from utils.logger import logger

# Global in-memory checkpointer for thread execution snapshots and human-in-the-loop resume
memory_checkpointer = MemorySaver()

def get_checkpointer():
    """Returns configured LangGraph checkpointer instance."""
    logger.info("Initialized LangGraph MemorySaver checkpointer for thread persistence.")
    return memory_checkpointer
