import json
from datetime import date
from typing import Annotated

import docker
from fastapi import FastAPI, Header

import requests
import os

from src.schemas import RUNTIMES, USER_PATH, HandlerData, JSONStructure
from src.strategy import ExecutorFactory, HandlerExecutionData

app = FastAPI()
client = docker.from_env()
timestamp = date.today().isoformat()


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": timestamp}

@app.post("/api/v1/run/{handler_id}")
async def run_handler(
    handler_id: str,
    x_pulse_key: Annotated[str | None, Header()] = None,
    data: JSONStructure = {},
):
    if x_pulse_key is None:
        return {"error": "Unauthorized"}, 401


    web_url = os.getenv("WEB_URL", "http://localhost:5173")
    response = requests.get(
        f"{web_url}/api/handler/{handler_id}",
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

        executor = ExecutorFactory.get_executor(handler_data.isAsync)

        result = await executor.execute(
            data=HandlerExecutionData(
                handler_id=handler_id,
                image=image,
                host_path=host_path,
                user_path=user_path,
                runtime=runtime,
                payload=payload_json,
            )
        )

        return result
    except Exception as e:
        return {"error": str(e)}, 500
