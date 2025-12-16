import json
import socket as pysocket
from datetime import date
from typing import Annotated, Any, Dict, List, Union

import docker
from fastapi import FastAPI, Header
from pydantic import BaseModel

import requests

app = FastAPI()
client = docker.from_env()
timestamp = date.today().isoformat()


class HandlerData(BaseModel):
    id: str
    name: str
    fileName: str
    filePath: str
    runtime: str
    isAsync: bool


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": timestamp}


JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

RUNTIMES = {
    "python": "python-runtime",
    "typescript": "typescript-runtime",
}

USER_PATH = {
    "python": "/app/user_function.py",
    "typescript": "/app/user_function.ts",
}


@app.post("/api/v1/run/{handler_id}")
async def run_handler(
    handler_id: str,
    x_pulse_key: Annotated[str | None, Header()] = None,
    data: JSONStructure = {},
):
    if x_pulse_key is None:
        return {"error": "Unauthorized"}, 401

    response = requests.get(
        f"http://localhost:5173/api/handler/{handler_id}",
        headers={"x-pulse-key": x_pulse_key},
    )

    if response.status_code != 200:
        return {"error": "Failed to run handler"}, response.status_code

    handler_data = HandlerData.model_validate(response.json())

    payload_json = json.dumps(data)
    host_path = handler_data.filePath

    try:
        runtime = handler_data.runtime
        image = RUNTIMES.get(runtime)
        user_path = USER_PATH.get(runtime)
        if image is None:
            return {"error": f"Unsupported runtime: {runtime}"}, 400

        if user_path is None:
            return {"error": f"Unsupported runtime path: {runtime}"}, 400

        container = client.containers.run(
            image=image,
            volumes={host_path: {"bind": user_path, "mode": "ro,Z"}},
            stdin_open=True,
            detach=True,
            network_disabled=True,
            mem_limit="128m",
            nano_cpus=500000000,  # 0.5 CPU
        )

        print("Container started with ID:", container.id)

        socket = container.attach_socket(params={"stdin": 1, "stream": 1})
        socket._sock.sendall(payload_json.encode("utf-8"))
        socket._sock.shutdown(pysocket.SHUT_WR)
        socket._sock.close()

        container.wait()

        logs = container.logs(stdout=True, stderr=False)
        container.remove()
        return logs

    except Exception as e:
        return {"error": str(e)}, 500
