from fastapi import FastAPI, HTTPException

from jarvis_injector.runtime.service import InjectorRuntime


def register_target_routes(app: FastAPI, runtime: InjectorRuntime) -> None:
    @app.get("/api/targets")
    def list_targets():
        return [target.model_dump(mode="json") for target in runtime.target_registry.summaries()]

    @app.post("/api/targets/{target_id}/probe")
    def probe_target(target_id: str):
        try:
            return runtime.probe_target(target_id).model_dump(mode="json")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown target '{target_id}'") from exc

