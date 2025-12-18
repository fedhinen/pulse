import asyncio
import json
import uuid
from datetime import datetime
from time import time
from typing import Any, Dict

import psycopg2
from aio_pika import connect_robust
from psycopg2.extras import Json  # Importante para JSONB

psql = psycopg2.connect(
    database="local",
    user="root",
    host="localhost",
    password="mysecretpassword",
    port=5432,
)


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
                    print(handler_log)
                    cur.execute(
                        """INSERT INTO handler_logs (id, handler_id, logs, start_at, end_at) VALUES (%s, %s, %s, %s, %s)""",
                        handler_log,
                    )
                    psql.commit()

                    handler_exec = (
                        str(uuid.uuid7()),
                        handler_id,
                        Json(data.get("response") or {}),
                        "FINISHED",
                        str(log_id),
                    )
                    print(handler_exec)
                    cur.execute(
                        """INSERT INTO handler_exec (id, handler_id, response, status, log_id) VALUES (%s, %s, %s, %s, %s)""",
                        handler_exec,
                    )
                    psql.commit()
                except Exception as e:
                    print(f"Error in worker {e}")


if __name__ == "__main__":
    try:
        asyncio.run(logs_synchronous())
    except KeyboardInterrupt:
        print("Worker detenido")
