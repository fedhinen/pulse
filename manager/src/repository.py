from dataclasses import astuple, dataclass
from datetime import datetime
import asyncpg


@dataclass
class HandlerLogEntry:
    log_id: str
    handler_id: str
    logs: str
    start_at: datetime
    end_at: datetime


@dataclass
class HandlerExecEntry:
    exec_id: str
    handler_id: str
    response: str
    status: str
    log_id: str | None


@dataclass
class HandlerExecUpdate:
    status: str
    response: str
    log_id: str | None
    exec_id: str


class RepositoryMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Repository(metaclass=RepositoryMeta):

    def __init__(self):
        self.db_pool: asyncpg.Pool | None = None

    async def connect(self):
        if self.db_pool:
            return
        
        self.db_pool = await asyncpg.create_pool(
            min_size=1,
            max_size=10,
            database="local",
            user="root",
            host="localhost",
            password="mysecretpassword",
            port=5432,
        )

    async def _raw_executor_sync(self, statement: str, *args):
        if self.db_pool is None:
            raise Exception("Database pool not established")
        
        
        async with self.db_pool.acquire() as connection:
            await connection.execute(statement, *args)
        return args

    async def raw_executor(self, statement: str, params: tuple = ()):
        if self.db_pool is None:
            await self.connect()
        
        return await self._raw_executor_sync(statement, *params)

    async def insert_handler_exec(self, data: HandlerExecEntry):
        insert_statement = """
        INSERT INTO handler_exec (id, handler_id, response, status, log_id) VALUES ($1, $2, $3, $4, $5)
        """

        await self.raw_executor(insert_statement, astuple(data))

        return data

    async def insert_handler_logs(self, data: HandlerLogEntry):
        insert_statement = """
        INSERT INTO handler_logs (id, handler_id, logs, start_at, end_at) VALUES ($1, $2, $3, $4, $5)
        """

        await self.raw_executor(insert_statement, astuple(data))

        return data

    async def update_handler_exec(self, data: HandlerExecUpdate):
        update_statement = """
        UPDATE handler_exec SET status = $1, response = $2, log_id = $3 WHERE id = $4
        """
        await self.raw_executor(update_statement, astuple(data))
        return data


repository = Repository()
