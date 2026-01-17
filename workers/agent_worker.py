"""
Agent worker - Background worker for running agent tasks
"""
import asyncio
from typing import Optional
from agents.graph import create_agent_graph, AgentState


class AgentWorker:
    """
    Background worker for processing agent tasks.
    Runs LangGraph workflows asynchronously.
    """
    
    def __init__(self):
        self.graph = create_agent_graph()
        self.running = False
        self.task_queue: asyncio.Queue = asyncio.Queue()
    
    async def start(self):
        """Start the worker"""
        self.running = True
        await self._process_loop()
    
    async def stop(self):
        """Stop the worker"""
        self.running = False
    
    async def enqueue(self, session_id: str, telemetry: dict):
        """Add a task to the processing queue"""
        await self.task_queue.put({
            "session_id": session_id,
            "telemetry": telemetry,
        })
    
    async def _process_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                await self._process_task(task)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error in agent worker: {e}")
    
    async def _process_task(self, task: dict):
        """Process a single task through the agent graph"""
        initial_state: AgentState = {
            "session_id": task["session_id"],
            "motor_state": "idle",
            "motor_confidence": 0.0,
            "genre_weights": {},
            "context_analysis": {},
            "variance_audit": {},
            "stability_proposal": {},
            "exploratory_proposal": {},
            "final_layout_directive": {},
        }
        
        # Run the graph
        result = await self.graph.ainvoke(initial_state)
        
        # TODO: Push layout update via WebSocket/SSE
        print(f"Layout generated for session {task['session_id']}")
        
        return result


agent_worker = AgentWorker()
