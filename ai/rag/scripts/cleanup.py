import os
import sys
import logging
logger = logging.getLogger(__name__)
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
from ai.rag.pipeline import CleanupManager
USAGE = "Usage: python rag/scripts/cleanup.py <target>\n\nTargets:\n  [None]        Delete all generated RAG data (default)\n  chunks        Delete generated chunk files\n  embeddings    Delete generated embedding files\n  vector_store  Delete the FAISS vector store\n  all           Delete all generated RAG data\n"
if __name__ == "__main__":
    if len(sys.argv) < 2:
        action = "all"
    else:
        action = sys.argv[1].lower()
        if action.startswith("--"):
            action = action[2:]
        elif action.startswith("-"):
            action = action[1:]
    if action == "chunks":
        CleanupManager.cleanup_chunks()
    elif action == "embeddings":
        CleanupManager.cleanup_embeddings()
    elif action == "vector_store":
        CleanupManager.cleanup_vector_store()
    elif action == "all":
        CleanupManager.cleanup_all()
    else:
        logger.info(f"Unknown target: {action}")
        logger.info(USAGE)
        sys.exit(1)