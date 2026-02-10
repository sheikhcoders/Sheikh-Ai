from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.sandbox_manager import sandbox_manager
from backend.agent import get_or_create_agent
import asyncio
import json

app = FastAPI(title="Sheikh-Ai Main Server")
security = HTTPBearer()

class CreateAgentRequest(BaseModel):
    user_id: str

class MessageRequest(BaseModel):
    session_id: str
    message: str

class StopRequest(BaseModel):
    session_id: str

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Basic token verification for demonstration
    if credentials.credentials != "secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return credentials.credentials

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/agent/create")
async def create_agent(request: CreateAgentRequest, token: str = Depends(verify_token)):
    try:
        session_id, sandbox_info = sandbox_manager.create_sandbox()
        return {
            "session_id": session_id,
            "status": "created",
            "ports": sandbox_info["ports"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/message")
async def send_message(request: MessageRequest, token: str = Depends(verify_token)):
    # Retrieve sandbox port for this session
    sandbox_info = sandbox_manager.sandboxes.get(request.session_id)
    if not sandbox_info:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = get_or_create_agent(request.session_id, sandbox_port=sandbox_info["ports"]["api"])
    # Process message in background
    asyncio.create_task(agent.process_message(request.message))
    return {"status": "message_received"}

@app.get("/events/{session_id}")
async def get_events(session_id: str):
    sandbox_info = sandbox_manager.sandboxes.get(session_id)
    if not sandbox_info:
        raise HTTPException(status_code=404, detail="Session not found")

    agent = get_or_create_agent(session_id, sandbox_port=sandbox_info["ports"]["api"])
    return StreamingResponse(agent.event_generator(), media_type="text/event-stream")

@app.post("/agent/stop")
async def stop_agent(request: StopRequest, token: str = Depends(verify_token)):
    sandbox_manager.stop_sandbox(request.session_id)
    if request.session_id in agents:
        del agents[request.session_id]
    return {"status": "stopped"}

@app.post("/mcp/execute")
async def execute_mcp(request: dict, token: str = Depends(verify_token)):
    # Stub for Model Context Protocol integration
    return {"status": "success", "message": "MCP tool execution stub called", "input": request}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
