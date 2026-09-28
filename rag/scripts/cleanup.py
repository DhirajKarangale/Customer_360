import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rag.pipeline import CleanupManager

USAGE = """Usage: python rag/scripts/cleanup.py <target>

Targets:
  [None]        Delete all generated RAG data (default)
  chunks        Delete generated chunk files
  embeddings    Delete generated embedding files
  vector_store  Delete the FAISS vector store
  all           Delete all generated RAG data
"""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        action = "all"
    else:
        action = sys.argv[1].lower()
        # Handle arguments passed with flags, like --all or -chunks
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
        print(f"Unknown target: {action}")
        print(USAGE)
        sys.exit(1)
