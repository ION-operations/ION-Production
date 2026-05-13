from fastapi import FastAPI, HTTPException

from jarvis_injector.core.models import DispatchRequest
from jarvis_injector.runtime.service import InjectorRuntime


def register_dispatch_routes(app: FastAPI, runtime: InjectorRuntime) -> None:
    @app.post("/api/dispatch")
    def dispatch(request: DispatchRequest):
        try:
            return runtime.dispatch_service.submit(request).model_dump(mode="json")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/executions/{execution_id}")
    def get_execution(execution_id: str):
        record = runtime.dispatch_service.get_execution(execution_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Unknown execution '{execution_id}'")
        return record.model_dump(mode="json")

    @app.get("/api/executions")
    def list_executions(limit: int = 25):
        return [record.model_dump(mode="json") for record in runtime.dispatch_service.list_executions(limit=limit)]

