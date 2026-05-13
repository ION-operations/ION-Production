from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from jarvis_injector.api.routes_capture import register_capture_routes
from jarvis_injector.api.routes_artifacts import register_artifact_routes
from jarvis_injector.api.routes_dispatch import register_dispatch_routes
from jarvis_injector.api.routes_health import register_health_routes
from jarvis_injector.api.routes_targets import register_target_routes
from jarvis_injector.runtime.service import InjectorRuntime


def create_api_server(runtime: InjectorRuntime) -> FastAPI:
    app = FastAPI(
        title="JARVIS Injector Runtime",
        version="0.1.0",
        description="Local Windows computer-action runtime for AIM-OS",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["null"],
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_health_routes(app, runtime)
    register_target_routes(app, runtime)
    register_dispatch_routes(app, runtime)
    register_capture_routes(app, runtime)
    register_artifact_routes(app, runtime)
    return app
