import importlib.util
import json
import sys
import traceback


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

        if hasattr(user_module, "handler"):
            result = user_module.handler(event)
            print(json.dumps({"status": "success", "output": result}))
        else:
            raise Exception("No handler function found in user_module")

    except Exception as e:
        error_msg = traceback.format_exc()
        print(json.dumps({"status": "error", "error": str(e), "trace": error_msg}))


if __name__ == "__main__":
    run()
