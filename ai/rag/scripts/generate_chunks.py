import os
import sys
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
from ai.rag.pipeline import ChunkGenerationPipeline
if __name__ == "__main__":
    pipeline = ChunkGenerationPipeline()
    pipeline.run()