import httpx
import time
import subprocess
import os
import sys
from unittest.mock import MagicMock, patch

def test_server():
    # Mocking Docker and SandboxManager for the test
    with patch('docker.from_env'), patch('backend.sandbox_manager.SandboxManager.create_sandbox') as mock_create:
        mock_create.return_value = ("test-session", {"ports": {"api": 8080, "vnc": 5900, "novnc": 6080, "cdp": 9222}})

        print("Starting main server...")
        server_process = subprocess.Popen(
            [sys.executable, "backend/server.py"],
            env={**os.environ, "SESSION_DB_TYPE": "file"}
        )
        time.sleep(3)

        try:
            base_url = "http://127.0.0.1:8000"
            headers = {"Authorization": "Bearer secret-token"}

            # Test health
            print("Testing health...")
            response = httpx.get(f"{base_url}/health")
            assert response.status_code == 200

            # Test agent create
            print("Testing agent create...")
            response = httpx.post(f"{base_url}/agent/create", json={"user_id": "user1"}, headers=headers)
            print(f"Agent create: {response.json()}")
            assert response.status_code == 200
            session_id = response.json()["session_id"]

            # Test agent message
            print("Testing agent message...")
            response = httpx.post(f"{base_url}/agent/message", json={"session_id": session_id, "message": "hello"}, headers=headers)
            assert response.status_code == 200

            # Test events (SSE)
            print("Testing events...")
            # We just check if we can connect
            with httpx.stream("GET", f"{base_url}/events/{session_id}") as r:
                assert r.status_code == 200
                print("SSE connection successful")

            print("Tests passed successfully!")

        except Exception as e:
            print(f"Tests failed: {e}")
            sys.exit(1)
        finally:
            print("Shutting down server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    test_server()
