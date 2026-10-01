import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.agent.run import invoke_agent

response = invoke_agent("Can you find any emails where customer ID a0cfc835-3fa7-4c2d-8ce3-68ea56373eb5 mentioned renewing their policy?")
print("FINAL RESPONSE:", response)
