from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import subprocess
from playwright.async_api import async_playwright

# Set DISPLAY for Xvfb
os.environ["DISPLAY"] = ":99"

app = FastAPI(title="Sandbox API")

class FileInfo(BaseModel):
    name: str
    is_dir: bool
    size: Optional[int] = None

class WriteFileRequest(BaseModel):
    path: str
    content: str

class CommandRequest(BaseModel):
    command: str
    timeout: int = 30

class BrowserRequest(BaseModel):
    url: str

class ClickRequest(BaseModel):
    selector: str

class TypeRequest(BaseModel):
    selector: str
    text: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/llms.txt", response_class=PlainTextResponse)
async def get_llms_txt():
    content = """# Sheikh-Ai Sandbox API

This API provides a sandboxed Ubuntu environment for AI agents.

## Core Capabilities
- File Management: List, read, write, and delete files.
- Shell Execution: Run arbitrary bash commands.
- Browser Automation: Control a Chrome browser via Playwright.

## Key Endpoints
- /files: CRUD operations on the filesystem.
- /shell/execute: Bash command execution.
- /browser: Navigate, screenshot, click, and type.
"""
    return content

@app.get("/llms-full.txt", response_class=PlainTextResponse)
async def get_llms_full_txt():
    content = """# Sheikh-Ai Sandbox API Documentation

Detailed documentation of the Sheikh-Ai Sandbox API for LLM consumption.

## Filesystem Tools
- GET /files/list?path={path}: Returns a list of files and directories.
- GET /files/read?path={path}: Returns the text content of a file.
- POST /files/write: Writes content to a path. Body: {"path": "...", "content": "..."}
- DELETE /files/delete?path={path}: Deletes a file or directory.

## Shell Tools
- POST /shell/execute: Executes a bash command. Body: {"command": "...", "timeout": 30}
- Returns stdout, stderr, and return_code.

## Browser Tools
- POST /browser/goto: Navigates to a URL. Body: {"url": "..."}
- GET /browser/screenshot: Takes a PNG screenshot and returns the path.
- POST /browser/click: Clicks an element by selector. Body: {"selector": "..."}
- POST /browser/type: Fills an input. Body: {"selector": "...", "text": "..."}

## Environment
- OS: Ubuntu 22.04
- Browser: Chromium (Playwright)
- Display: Xvfb (:99)
- VNC: Available on port 6080
"""
    return content

@app.get("/tools")
async def get_tools():
    return {
        "tools": [
            {
                "name": "list_files",
                "description": "List files and directories in the sandbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The directory path to list"}
                    }
                }
            },
            {
                "name": "read_file",
                "description": "Read the content of a file in the sandbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The file path to read"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file in the sandbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "The file path to write to"},
                        "content": {"type": "string", "description": "The content to write"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "execute_command",
                "description": "Execute a bash command in the sandbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "The bash command to execute"},
                        "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "browser_goto",
                "description": "Navigate to a URL in the sandbox browser",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The URL to navigate to"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "browser_screenshot",
                "description": "Take a screenshot of the current page in the sandbox browser",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }

@app.get("/files/list", response_model=List[FileInfo])
async def list_files(path: str = "."):
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Path not found")
        items = os.listdir(path)
        result = []
        for item in items:
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)
            try:
                size = os.path.getsize(full_path) if not is_dir else None
            except OSError:
                size = None
            result.append(FileInfo(name=item, is_dir=is_dir, size=size))
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/read")
async def read_file_api(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    if os.path.isdir(path):
        raise HTTPException(status_code=400, detail="Path is a directory")
    try:
        with open(path, "r") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/files/write")
async def write_file_api(request: WriteFileRequest):
    try:
        dir_name = os.path.dirname(request.path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(request.path, "w") as f:
            f.write(request.content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/delete")
async def delete_file_api(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/shell/execute")
async def execute_command(request: CommandRequest):
    try:
        process = subprocess.run(
            request.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=request.timeout
        )
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Browser state
state = {
    "playwright": None,
    "browser": None,
    "context": None,
    "page": None
}

async def get_page():
    if state["page"] is None:
        state["playwright"] = await async_playwright().start()
        state["browser"] = await state["playwright"].chromium.launch(headless=False)
        state["context"] = await state["browser"].new_context()
        state["page"] = await state["context"].new_page()
    return state["page"]

@app.post("/browser/goto")
async def browser_goto(request: BrowserRequest):
    try:
        page = await get_page()
        await page.goto(request.url)
        return {"status": "success", "url": page.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/browser/screenshot")
async def browser_screenshot():
    try:
        page = await get_page()
        screenshot_path = "screenshot.png"
        await page.screenshot(path=screenshot_path)
        return {"status": "success", "path": screenshot_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/click")
async def browser_click(request: ClickRequest):
    try:
        page = await get_page()
        await page.click(request.selector)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/type")
async def browser_type(request: TypeRequest):
    try:
        page = await get_page()
        await page.fill(request.selector, request.text)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    if state["browser"]:
        await state["browser"].close()
    if state["playwright"]:
        await state["playwright"].stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
