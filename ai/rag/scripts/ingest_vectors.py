import os
import sys
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
from ai.rag.pipeline import VectorIngestionPipeline
if __name__ == "__main__":
    pipeline = VectorIngestionPipeline()
    pipeline.run()