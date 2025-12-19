from dataclasses import dataclass
import json
import time
from typing_extensions import Self
import docker
import socket as pysocket


@dataclass
class ContainerRun:
    image: str
    host_path: str
    user_path: str
    payload: str
    handler_id: str

class ContainerRunner:
    _instance = None
    _client = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(ContainerRunner, cls).__new__(cls)

            cls._client = docker.from_env()
        return cls._instance
    
    async def run(self, container_data: ContainerRun):
        try:
            if self._client is None:
                raise Exception("Docker client not initialized")
        
            start_time = time.time()
            container = self._client.containers.run(
                image=container_data.image,
                volumes={container_data.host_path: {"bind": container_data.user_path, "mode": "ro,Z"}},
                stdin_open=True,
                detach=True,
                network_disabled=True,
                mem_limit="128m",
                nano_cpus=500000000,  # 0.5 CPU
            )

            socket = container.attach_socket(params={"stdin": 1, "stream": 1})
            socket._sock.sendall(container_data.payload.encode("utf-8"))
            socket._sock.shutdown(pysocket.SHUT_WR)
            socket._sock.close()

            container.wait()

            handler_result_raw = container.logs(stdout=True, stderr=False)
            handler_logs_raw = container.logs(stdout=False, stderr=True)

            handler_logs = handler_logs_raw.decode("utf-8") if handler_logs_raw else ""
            handler_json = json.loads(handler_result_raw.decode("utf-8")) if handler_result_raw else {}

            container.remove()
            end_time = time.time()
            
            return {
                "response": handler_json,
                "logs": handler_logs,
                "start_time": start_time,
                "end_time": end_time,
            } 
        except Exception as e:
            raise e