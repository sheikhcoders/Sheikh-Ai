import httpx
import time
import subprocess
import os
import sys

def test_api():
    # Start the server in background
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    time.sleep(3) # Wait for server to start

    try:
        base_url = "http://127.0.0.1:8001"

        # Test health
        print("Testing health...")
        response = httpx.get(f"{base_url}/health")
        print(f"Health check: {response.json()}")
        assert response.status_code == 200

        # Test file write
        print("Testing file write...")
        response = httpx.post(f"{base_url}/files/write", json={"path": "test.txt", "content": "hello world"})
        print(f"File write: {response.json()}")
        assert response.status_code == 200

        # Test file list
        print("Testing file list...")
        response = httpx.get(f"{base_url}/files/list", params={"path": "."})
        print(f"File list: {response.json()}")
        assert any(item['name'] == 'test.txt' for item in response.json())

        # Test file read
        print("Testing file read...")
        response = httpx.get(f"{base_url}/files/read", params={"path": "test.txt"})
        print(f"File read: {response.json()}")
        assert response.json()["content"] == "hello world"

        # Test shell execute
        print("Testing shell execute...")
        response = httpx.post(f"{base_url}/shell/execute", json={"command": "echo 'hello from shell'"})
        print(f"Shell execute: {response.json()}")
        assert "hello from shell" in response.json()["stdout"]

        # Test llms.txt
        print("Testing llms.txt...")
        response = httpx.get(f"{base_url}/llms.txt")
        print(f"llms.txt: {response.text[:50]}...")
        assert response.status_code == 200
        assert "# Sheikh-Ai Sandbox API" in response.text

        # Test llms-full.txt
        print("Testing llms-full.txt...")
        response = httpx.get(f"{base_url}/llms-full.txt")
        print(f"llms-full.txt: {response.text[:50]}...")
        assert response.status_code == 200
        assert "# Sheikh-Ai Sandbox API Documentation" in response.text

        # Test /tools
        print("Testing /tools...")
        response = httpx.get(f"{base_url}/tools")
        print(f"tools: {len(response.json()['tools'])} tools found.")
        assert response.status_code == 200
        assert len(response.json()["tools"]) >= 6

        print("Tests passed successfully!")

    except Exception as e:
        print(f"Tests failed: {e}")
        sys.exit(1)
    finally:
        print("Shutting down server...")
        server_process.terminate()
        server_process.wait()
        test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.txt")
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_api()
