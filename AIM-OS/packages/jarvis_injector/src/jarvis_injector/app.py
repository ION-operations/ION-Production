from jarvis_injector.api.server import create_api_server
from jarvis_injector.runtime.service import build_runtime


def build_application():
    runtime = build_runtime()
    return create_api_server(runtime)

