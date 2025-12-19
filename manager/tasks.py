import asyncio
import json
import uuid
from datetime import datetime
from time import time
from typing import Any, Dict
from psycopg2.extras import Json

from src.container import ContainerRun, ContainerRunner
from src.schemas import AsynchronousExecData
from src.worker import broker
from src.repository import (
    repository,
    HandlerExecEntry,
    HandlerExecUpdate,
    HandlerLogEntry,
)


async def logs():
    channel = await broker.worker()

    queue = await channel.declare_queue("logs")
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

                    handler_log = HandlerLogEntry(
                        log_id=str(log_id),
                        handler_id=handler_id,
                        logs=Json(data.get("logs") or {}),
                        start_at=start_at,
                        end_at=end_at,
                    )

                    await repository.insert_handler_logs(handler_log)

                    if exec_id is None:
                        handler_exec = HandlerExecEntry(
                            exec_id=str(uuid.uuid7()),
                            handler_id=handler_id,
                            response=Json(data.get("response") or {}),
                            status="FINISHED",
                            log_id=str(log_id),
                        )
                        await repository.insert_handler_exec(handler_exec)
                    else:
                        handler_exec_update = HandlerExecUpdate(
                            status="FINISHED",
                            response=Json(data.get("response") or {}),
                            log_id=str(log_id),
                            exec_id=str(exec_id),
                        )
                        await repository.update_handler_exec(handler_exec_update)

                except Exception as e:
                    print(f"Error in worker {e}")


async def asynchronous_exec():
    channel = await broker.worker()

    queue = await channel.declare_queue("asynchronous_exec")

    runner = ContainerRunner()

    async with queue.iterator() as q_iter:
        async for message in q_iter:
            async with message.process():
                try:
                    data: Dict[str, Any] = json.loads(message.body.decode())

                    validated_data = AsynchronousExecData.model_validate(data)

                    handler_exec = HandlerExecUpdate(
                        status="PROGRESS",
                        exec_id=str(validated_data.exec_id),
                        response=Json({}),
                        log_id=None,
                    )

                    await repository.update_handler_exec(handler_exec)

                    result = await runner.run(ContainerRun(
                        image=validated_data.image,
                        host_path=validated_data.host_path,
                        user_path=validated_data.user_path,
                        payload=validated_data.payload,
                        handler_id=validated_data.handler_id,
                    ))

                    synchronized_exec_data = {
                        "exec_id": validated_data.exec_id,
                        "end_time": result["end_time"],
                        "start_time": result["start_time"],
                        "logs": result["logs"],
                        "response": result["response"],
                        "handler_id": validated_data.handler_id,
                    }

                    await broker.publish(synchronized_exec_data, "logs")

                except Exception as e:
                    print(f"Error in asynchronous exec worker {e}")


async def main():
    await broker.connect()
    try:
        await asyncio.gather(
            logs(),
            asynchronous_exec(),
        )
    finally:
        await broker.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker detenido")
