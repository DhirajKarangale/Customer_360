import asyncio
from typing import Dict, List

class SSEManager:
    def __init__(self):
        # Maps insurance_agent_id to a list of asyncio Queues
        self.connections: Dict[str, List[asyncio.Queue]] = {}

    async def connect(self, agent_id: str) -> asyncio.Queue:
        if agent_id not in self.connections:
            self.connections[agent_id] = []
        queue = asyncio.Queue()
        self.connections[agent_id].append(queue)
        return queue

    def disconnect(self, agent_id: str, queue: asyncio.Queue):
        if agent_id in self.connections:
            if queue in self.connections[agent_id]:
                self.connections[agent_id].remove(queue)
            if not self.connections[agent_id]:
                del self.connections[agent_id]

    def publish(self, agent_id: str, message: dict):
        if agent_id in self.connections:
            for queue in self.connections[agent_id]:
                try:
                    queue.put_nowait(message)
                except asyncio.QueueFull:
                    pass

# Global singleton
sse_manager = SSEManager()
