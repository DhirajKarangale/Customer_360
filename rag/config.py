import os
from dotenv import load_dotenv

_RAG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_RAG_DIR)

_env_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)

# ── Source Data ──
CLEANED_DATA_DIR = os.path.join(
    PROJECT_ROOT, "data_generation", "interactions_data", "cleaned"
)

# ── Intermediate Storage ──
CHUNKS_DATA_DIR = os.path.join(_RAG_DIR, "chunks_data")
EMBEDDINGS_DATA_DIR = os.path.join(_RAG_DIR, "embeddings_data")
VECTOR_STORE_DIR = os.path.join(_RAG_DIR, "vector_store_data")

# ── Override Behavior ──
OVERRIDE_CHUNKS = False
OVERRIDE_EMBEDDINGS = False
DIRECT_EMBEDDING_NO_CHUNKING = True

# ── Embedding ──
EMBEDDING_MODEL = "snowflake-arctic-embed-l-v2.0"
# EMBEDDING_MODEL = "voyage-multilingual-2"
EMBEDDING_DIMENSION = 1024
EMBEDDING_MIN_DELAY_SECONDS = 7
EMBEDDING_MAX_DELAY_SECONDS = 15

# ── Chunking ──
CHUNK_SIZE = 1500
CHUNK_OVERLAP = int(CHUNK_SIZE * 0.10)

# ── Retrieval ──
TOP_K = 5
SIMILARITY_SCORE_THRESHOLD = 0.3
