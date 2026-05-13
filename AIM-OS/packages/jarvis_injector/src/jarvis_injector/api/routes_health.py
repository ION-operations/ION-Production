from fastapi import FastAPI

from jarvis_injector.runtime.service import InjectorRuntime


def register_health_routes(app: FastAPI, runtime: InjectorRuntime) -> None:
    @app.get("/health")
    def health():
        return runtime.health().model_dump(mode="json")

