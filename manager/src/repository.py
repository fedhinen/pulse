import asyncio
from contextlib import contextmanager
from dataclasses import astuple, dataclass
from datetime import datetime
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import Json  # Importante para JSONB


@dataclass
class HandlerLogEntry:
    log_id: str
    handler_id: str
    logs: Json
    start_at: datetime
    end_at: datetime


@dataclass
class HandlerExecEntry:
    exec_id: str
    handler_id: str
    response: Json
    status: str
    log_id: str | None


@dataclass
class HandlerExecUpdate:
    status: str
    response: Json
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
        self.db_pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            database="local",
            user="root",
            host="localhost",
            password="mysecretpassword",
            port=5432,
        )
        self.connection = psycopg2.connect(
            database="local",
            user="root",
            host="localhost",
            password="mysecretpassword",
            port=5432,
        )

    @contextmanager
    def _get_db_cursor(self):
        conn = self.db_pool.getconn()
        try:
            with conn.cursor() as cursor:
                yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.db_pool.putconn(conn)

    def _raw_executor_sync(self, statement: str, params: tuple = ()):
        with self._get_db_cursor() as cursor:
            cursor.execute(statement, params)
        return params

    async def raw_executor(self, statement: str, params: tuple = ()):
        return await asyncio.to_thread(self._raw_executor_sync, statement, params)

    async def insert_handler_exec(self, data: HandlerExecEntry):
        insert_statement = """
        INSERT INTO handler_exec (id, handler_id, response, status, log_id) VALUES (%s, %s, %s, %s, %s)
        """

        await self.raw_executor(insert_statement, astuple(data))

        return data

    async def insert_handler_logs(self, data: HandlerLogEntry):
        insert_statement = """
        INSERT INTO handler_logs (id, handler_id, logs, start_at, end_at) VALUES (%s, %s, %s, %s, %s)
        """

        await self.raw_executor(insert_statement, astuple(data))

        return data

    async def update_handler_exec(self, data: HandlerExecUpdate):
        update_statement = """
        UPDATE handler_exec SET status = %s, response = %s, log_id = %s WHERE id = %s
        """
        await self.raw_executor(update_statement, astuple(data))
        return data


repository = Repository()
