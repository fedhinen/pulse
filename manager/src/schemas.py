from typing import Any, Dict, List, Union

from pydantic import BaseModel

RUNTIMES = {
    "python": "python-runtime",
    "typescript": "typescript-runtime",
}

USER_PATH = {
    "python": "/app/user_function.py",
    "typescript": "/app/user_function.ts",
}

JSONObject = Dict[Any, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

class HandlerData(BaseModel):
    id: str
    name: str
    fileName: str
    filePath: str
    runtime: str
    isAsync: bool

class AsynchronousExecData(BaseModel):
    runtime: str
    image: str
    user_path: str
    host_path: str
    handler_id: str
    payload: str
    exec_id: str