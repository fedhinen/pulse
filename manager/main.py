import asyncio
import json
import socket as pysocket
from datetime import date
from time import time
from typing import Annotated, Any, Dict, List, Union

import docker
import psycopg2
from aio_pika import DeliveryMode, Message, connect_robust
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


async def publish_message(message: Dict[str, Any], key: str):
    try:
        connection = await connect_robust("amqp://pulse:pulse@127.0.0.1")
        channel = await connection.channel()

        await channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=key,
        )
        await connection.close()
    except Exception as e:
        print("Error in publish message", e)


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

        if handler_data.isAsync:
            ## BullMQ o RabbitMQ para manejar asincronía en el futuro
            return {"error": "Asynchronous handlers are not supported yet"}, 400

        start_time = time()
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

        handler_result_raw = container.logs(stdout=True, stderr=False)
        handler_logs_raw = container.logs(stdout=False, stderr=True)

        handler_logs = handler_logs_raw.decode("utf-8") if handler_logs_raw else ""
        print(handler_logs)

        container.remove()
        end_time = time()

        json_response = (
            json.loads(handler_result_raw.decode("utf-8")) if handler_result_raw else {}
        )

        synchronized_exec_data = {
            "end_time": end_time,
            "start_time": start_time,
            "logs": handler_logs,
            "response": json_response,
            "handler_id": handler_id,
        }

        await publish_message(synchronized_exec_data, "logs_synchronous")

        try:
            return json_response
        except Exception:
            return handler_result

    except Exception as e:
        return {"error": str(e)}, 500
