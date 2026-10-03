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

from ai.rag.pipeline import EmbeddingGenerationPipeline
from ai.utils.sf_auth import get_snowflake_conn

if __name__ == "__main__":
    logger.info("Connecting to Snowflake...")
    sf_conn = get_snowflake_conn()
    pipeline = EmbeddingGenerationPipeline()
    pipeline.run()
