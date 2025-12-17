import importlib.util
import io
import json
import sys
import traceback


class RedirectStd:
    def __init__(self, stdout=None, stderr=None):
        self.__stdout = stdout or sys.stdout
        self.__stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stderr.flush()
        self.old_stdout.flush()
        sys.stdout, sys.stderr = (
            self.__stdout,
            self.__stderr,
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self.__stdout.flush()
        self.__stderr.flush()
        sys.stdout, sys.stderr = self.old_stdout, self.old_stderr


def run():
    try:
        input_data = sys.stdin.read()
        event = json.loads(input_data) if input_data else {}
    except Exception:
        event = {}

    try:
        spec = importlib.util.spec_from_file_location(
            "user_module", "/app/user_function.py"
        )

        if spec is None or spec.loader is None:
            raise Exception("Could not load user_module from /app/user_function.py")

        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        captura_stdout = io.StringIO()

        if hasattr(user_module, "handler"):
            with RedirectStd(stdout=captura_stdout):
                result = user_module.handler(event)

            allLogs = captura_stdout.getvalue()
            print(allLogs, file=sys.stderr)
            print(json.dumps({"status": "success", "output": result}), file=sys.stdout)
        else:
            raise Exception("No handler function found in user_module")

    except Exception as e:
        error_msg = traceback.format_exc()
        print(json.dumps({"status": "error", "error": str(e), "trace": error_msg}))


if __name__ == "__main__":
    run()
