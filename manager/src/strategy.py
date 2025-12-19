from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import dataclass
import uuid

from src.container import ContainerRun, ContainerRunner
from src.repository import HandlerExecEntry, repository
from src.worker import broker
from psycopg2.extras import Json  # Importante para JSONB


@dataclass
class HandlerExecutionData:
    runtime: str
    image: str
    user_path: str
    host_path: str
    handler_id: str
    payload: str


class ExecutorStrategy:
    @abstractmethod
    async def execute(self, data: HandlerExecutionData) -> dict:
        pass


class SynchronousStrategy(ExecutorStrategy):
    def __init__(self):
        self.container_runner = ContainerRunner()

    async def execute(self, data: HandlerExecutionData) -> dict:
        handler_json = await self.container_runner.run(
            ContainerRun(
                image=data.image,
                host_path=data.host_path,
                user_path=data.user_path,
                payload=data.payload,
                handler_id=data.handler_id,
            )
        )

        synchronized_exec_data = {
            "end_time": handler_json["end_time"],
            "start_time": handler_json["start_time"],
            "logs": handler_json["logs"],
            "response": handler_json["response"],
            "handler_id": data.handler_id,
        }

        await broker.publish(synchronized_exec_data, "logs")

        return handler_json["response"]


class AsynchronousStrategy(ExecutorStrategy):
    def __init__(self) -> None:
        self.container_runner = ContainerRunner()

    async def execute(self, data: HandlerExecutionData):
        exec_id = uuid.uuid7()

        handler_exec = HandlerExecEntry(
            exec_id=str(exec_id),
            handler_id=data.handler_id,
            response=Json({}),
            status="QUEUE",
            log_id=None,
        )

        await repository.insert_handler_exec(handler_exec)

        async_handler = {
            "runtime": data.runtime,
            "image": data.image,
            "user_path": data.user_path,
            "host_path": data.host_path,
            "handler_id": data.handler_id,
            "payload": data.payload,
            "exec_id": str(exec_id),
        }

        await broker.publish(async_handler, "asynchronous_exec")

        return {"exec_id": str(exec_id)}
    


class ExecutorFactory:
    @staticmethod
    def get_executor(is_async: bool) -> ExecutorStrategy:
        if is_async:
            return AsynchronousStrategy()
        else:
            return SynchronousStrategy()
