from dataclasses import astuple, dataclass
from datetime import datetime
import psycopg2
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
        self.connection = psycopg2.connect(
    database="local",
    user="root",
    host="localhost",
    password="mysecretpassword",
    port=5432,
)

    def raw_executor(self, statement: str, params: tuple = ()):
        cursor = self.connection.cursor()
        cursor.execute(statement, params)
        self.connection.commit()
        return params
    
    def insert_handler_exec(self, data: HandlerExecEntry):
        insert_statement = """
        INSERT INTO handler_exec (id, handler_id, response, status, log_id) VALUES (%s, %s, %s, %s, %s)
        """

        self.raw_executor(insert_statement, astuple(data))

        return data

    def insert_handler_logs(self, data: HandlerLogEntry):
        insert_statement = """
        INSERT INTO handler_logs (id, handler_id, logs, start_at, end_at) VALUES (%s, %s, %s, %s, %s)
        """

        self.raw_executor(insert_statement, astuple(data))

        return data

    def update_handler_exec(self, data: HandlerExecUpdate):
        update_statement = """
        UPDATE handler_exec SET status = %s, response = %s, log_id = %s WHERE id = %s
        """
        self.raw_executor(update_statement, astuple(data))

        return data
    
repository = Repository()