import os
from dotenv import load_dotenv

_RAG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_RAG_DIR)
_env_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)
CLEANED_DATA_DIR = os.path.join(
    PROJECT_ROOT, "data_generation", "interactions_data", "cleaned"
)
CHUNKS_DATA_DIR = os.path.join(_RAG_DIR, "chunks_data")
EMBEDDINGS_DATA_DIR = os.path.join(_RAG_DIR, "embeddings_data")
VECTOR_STORE_DIR = os.path.join(_RAG_DIR, "vector_store_data")
OVERRIDE_CHUNKS = False
OVERRIDE_EMBEDDINGS = False
DIRECT_EMBEDDING_NO_CHUNKING = True
EMBEDDING_MODEL = "EMBEDDING"
EMBEDDING_DIMENSION = 1024
EMBEDDING_MIN_DELAY_SECONDS = 7
EMBEDDING_MAX_DELAY_SECONDS = 15
CHUNK_SIZE = 1500
CHUNK_OVERLAP = int(CHUNK_SIZE * 0.1)
TOP_K = 5
SIMILARITY_SCORE_THRESHOLD = 0.1
