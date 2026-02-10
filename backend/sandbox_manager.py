import docker
import os
import uuid
import time

class SandboxManager:
    def __init__(self):
        self.client = docker.from_env()
        self.image_name = "sheikh-ai-sandbox"
        self.sandboxes = {}

    def create_sandbox(self, session_id=None):
        if not session_id:
            session_id = str(uuid.uuid4())

        # In a multi-agent scenario, we map to available host ports
        # We start searching from the requested default ports

        def find_available_port(start_port):
            import socket
            port = start_port
            while port < start_port + 1000:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('localhost', port)) != 0:
                        return port
                port += 1
            return None

        api_port = find_available_port(8080)
        vnc_port = find_available_port(5900)
        novnc_port = find_available_port(6080)
        cdp_port = find_available_port(9222)

        container = self.client.containers.run(
            self.image_name,
            detach=True,
            ports={
                '8080/tcp': api_port,
                '5900/tcp': vnc_port,
                '6080/tcp': novnc_port,
                '9222/tcp': cdp_port
            },
            volumes={
                '/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'},
                os.getcwd(): {'bind': '/app', 'mode': 'rw'}
            },
            name=f"sandbox-{session_id}",
            environment={
                "API_PORT": api_port,
                "VNC_PORT": vnc_port,
                "NOVNC_PORT": novnc_port,
                "CDP_PORT": cdp_port
            }
        )

        self.sandboxes[session_id] = {
            "container": container,
            "ports": {
                "api": api_port,
                "vnc": vnc_port,
                "novnc": novnc_port,
                "cdp": cdp_port
            }
        }
        return session_id, self.sandboxes[session_id]

    def stop_sandbox(self, session_id):
        if session_id in self.sandboxes:
            container = self.sandboxes[session_id]
            container.stop()
            container.remove()
            del self.sandboxes[session_id]

    def get_sandbox(self, session_id):
        return self.sandboxes.get(session_id)

sandbox_manager = SandboxManager()
