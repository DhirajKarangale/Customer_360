import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.agent.tools import get_database_context

print(get_database_context("b8626860-7a30-41c2-bad4-e14639f33c45"))
