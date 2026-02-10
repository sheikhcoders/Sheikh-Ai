from fastapi import FastAPI, HTTPException
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
