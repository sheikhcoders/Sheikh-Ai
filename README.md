# Sheikh-Ai

Sheikh-Ai is an advanced AI Agent System designed for complex workflows involving browser automation, code execution, and multi-agent coordination.

## Project Overview

This repository contains the core infrastructure for a sandboxed execution environment where AI agents can safely interact with a full Ubuntu system, including a web browser and a shell.

## Architecture

### Sandbox Environment
The sandbox is a Dockerized Ubuntu 22.04 environment that includes:
- **Graphical Support**: Xvfb for virtual frame buffer, x11vnc for VNC access, and websockify/noVNC for web-based VNC viewing.
- **Browser**: Google Chrome and Playwright for browser automation.
- **Process Management**: Supervisor is used to manage all background processes (X server, VNC server, API server).

### Sandbox API
A FastAPI-based control API provides an interface for the agent to:
- **File Operations**: Read, write, list, and delete files.
- **Shell Execution**: Run arbitrary shell commands with timeout control.
- **Browser Tools**: Navigate pages, take screenshots, and interact with web elements via Playwright.

## Project Structure

```
.
├── backend/
│   └── sandbox_api/          # FastAPI server implementation
├── docker/
│   └── sandbox/              # Dockerfile and Supervisor configuration
├── frontend/                 # Frontend application (in progress)
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Docker
- Python 3.10+ (for local development/testing)

### Running the Sandbox

To build and run the sandbox environment:

```bash
docker build -t sheikh-ai-sandbox -f docker/sandbox/Dockerfile .
docker run -p 8000:8000 -p 6080:6080 sheikh-ai-sandbox
```

- **API Server**: Accessible at `http://localhost:8000`
- **VNC (noVNC)**: Accessible at `http://localhost:6080/vnc.html`

## API Endpoints

- `GET /health`: Health check.
- `GET /files/list`: List files in a directory.
- `GET /files/read`: Read file content.
- `POST /files/write`: Write content to a file.
- `DELETE /files/delete`: Delete a file or directory.
- `POST /shell/execute`: Execute a shell command.
- `POST /browser/goto`: Navigate to a URL.
- `GET /browser/screenshot`: Take a screenshot of the current page.
- `POST /browser/click`: Click an element.
- `POST /browser/type`: Fill an input field.

## Testing

You can run the API tests locally (requires `fastapi`, `uvicorn`, `httpx` installed):

```bash
python backend/sandbox_api/test_api.py
```
