import httpx
import asyncio
import json
from backend.session_manager import session_manager

class PlanActAgent:
    def __init__(self, session_id, sandbox_url="http://localhost:8080"):
        self.session_id = session_id
        self.sandbox_url = sandbox_url
        self.queue = asyncio.Queue()

    async def process_message(self, message):
        # 1. Record user message event
        event = {"type": "user_message", "content": message}
        session_manager.save_event(self.session_id, event)
        await self.queue.put(event)

        # 2. Planning and Acting (Simplified for this task)
        # In a real system, this would call an LLM to decide which tools to use.
        # Here we will simulate tool calling based on the message.

        await self.log_agent_event("Thinking about the task...")

        if "search" in message.lower():
            await self.call_tool("search", {"query": message})
        elif "list files" in message.lower():
            await self.call_tool("list_files", {"path": "."})
        elif "browser" in message.lower():
            await self.call_tool("browser_goto", {"url": "https://www.google.com"})
        else:
            await self.log_agent_event(f"Received: {message}. I am a PlanAct Agent.")

    async def log_agent_event(self, content):
        event = {"type": "agent_log", "content": content}
        session_manager.save_event(self.session_id, event)
        await self.queue.put(event)

    async def call_tool(self, tool_name, params):
        await self.log_agent_event(f"Calling tool: {tool_name} with {params}")

        endpoint_map = {
            "search": "search",
            "list_files": "files/list",
            "read_file": "files/read",
            "write_file": "files/write",
            "execute_command": "shell/execute",
            "browser_goto": "browser/goto",
            "browser_screenshot": "browser/screenshot"
        }

        endpoint = f"{self.sandbox_url}/{endpoint_map.get(tool_name, tool_name)}"

        try:
            async with httpx.AsyncClient() as client:
                if tool_name in ["list_files", "read_file", "browser_screenshot"]:
                    response = await client.get(endpoint, params=params)
                else:
                    response = await client.post(endpoint, json=params)
                result = response.json()
        except Exception as e:
            result = {"status": "error", "message": str(e)}

        event = {"type": "tool_result", "tool": tool_name, "result": result}
        session_manager.save_event(self.session_id, event)
        await self.queue.put(event)
        return result

    async def event_generator(self):
        while True:
            event = await self.queue.get()
            yield f"data: {json.dumps(event)}\n\n"

agents = {}

def get_or_create_agent(session_id, sandbox_port=8080):
    if session_id not in agents:
        sandbox_url = f"http://localhost:{sandbox_port}"
        agents[session_id] = PlanActAgent(session_id, sandbox_url=sandbox_url)
    return agents[session_id]
