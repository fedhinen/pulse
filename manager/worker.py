import asyncio
import json
import uuid
from datetime import datetime
from time import time
from typing import Any, Dict
import socket as pysocket

import docker
import psycopg2
from aio_pika import DeliveryMode, Message, connect_robust
from psycopg2.extras import Json  # Importante para JSONB

client = docker.from_env()
psql = psycopg2.connect(
    database="local",
    user="root",
    host="localhost",
    password="mysecretpassword",
    port=5432,
)

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



async def logs_synchronous():
    connection = await connect_robust("amqp://pulse:pulse@127.0.0.1")
    channel = await connection.channel()

    queue = await channel.declare_queue("logs_synchronous")

    async with queue.iterator() as q_iter:
        async for message in q_iter:
            async with message.process():
                try:
                    data: Dict[str, Any] = json.loads(message.body.decode())

                    log_id = uuid.uuid7()
                    start_at = datetime.fromtimestamp(data.get("start_time") or time())
                    end_at = datetime.fromtimestamp(data.get("end_time") or time())
                    handler_id = data.get("handler_id")
                    exec_id = data.get("exec_id")

                    if handler_id is None:
                        continue

                    cur = psql.cursor()
                    handler_log = (
                        str(log_id),
                        handler_id,
                        Json(data.get("logs") or {}),
                        start_at,
                        end_at,
                    )
                    cur.execute(
                        """INSERT INTO handler_logs (id, handler_id, logs, start_at, end_at) VALUES (%s, %s, %s, %s, %s)""",
                        handler_log,
                    )
                    psql.commit()

    
                    if exec_id is None:
                        handler_exec = (
                            str(uuid.uuid7()),
                            handler_id,
                            Json(data.get("response") or {}),
                            "FINISHED",
                            str(log_id),
                        )
                        cur.execute(
                            """INSERT INTO handler_exec (id, handler_id, response, status, log_id) VALUES (%s, %s, %s, %s, %s)""",
                            handler_exec,
                        )
                        psql.commit()
                    else:
                        handler_exec_update = (
                            "FINISHED",
                            Json(data.get("response") or {}),
                            str(log_id),
                            str(exec_id),
                        )
                        cur.execute(
                            """UPDATE handler_exec SET status = %s, response = %s, log_id = %s WHERE id = %s""",
                            handler_exec_update,
                        )
                        psql.commit()

                except Exception as e:
                    print(f"Error in worker {e}")

async def asynchronous_exec():
    connection = await connect_robust("amqp://pulse:pulse@127.0.0.1")
    channel = await connection.channel()

    queue = await channel.declare_queue("asynchronous_exec")

    async with queue.iterator() as q_iter:
        async for message in q_iter:
            async with message.process():
                try:
                    data: Dict[str, Any] = json.loads(message.body.decode())

                    runtime = data.get("runtime")
                    image = data.get("image")
                    user_path = data.get("user_path")
                    host_path = data.get("host_path")
                    handler_id = data.get("handler_id")
                    payload_json = data.get("payload")
                    exec_id = data.get("exec_id")

                    if runtime is None or image is None or user_path is None or host_path is None or handler_id is None or payload_json is None or exec_id is None:
                        print("Invalid asynchronous exec data")
                        continue

                    cur = psql.cursor()
                    handler_exec = (
                        "PROGRESS",
                        str(exec_id),
                    )
                    cur.execute(
                        """UPDATE handler_exec SET status = %s WHERE id = %s""",
                        handler_exec,
                    )

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

                    print(f"Asynchronous exec completed for exec_id: {exec_id} {json_response}")

                    synchronized_exec_data = {
                        "exec_id": exec_id,
                        "end_time": end_time,
                        "start_time": start_time,
                        "logs": handler_logs,
                        "response": json_response,
                        "handler_id": handler_id,
                    }

                    await publish_message(synchronized_exec_data, "logs_synchronous")
                    print(f"Received asynchronous exec request: {data}")

                except Exception as e:
                    print(f"Error in asynchronous exec worker {e}")

async def main():
    await asyncio.gather(
        logs_synchronous(),
        asynchronous_exec(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker detenido")
