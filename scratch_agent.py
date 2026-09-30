import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.agent.run import invoke_agent

response = invoke_agent("Can you give me detail informatation about policy POL-1028-823")
print("FINAL RESPONSE:", response)
