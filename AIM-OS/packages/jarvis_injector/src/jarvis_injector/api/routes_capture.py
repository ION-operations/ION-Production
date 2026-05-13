from fastapi import FastAPI, HTTPException

from jarvis_injector.capture.models import CaptureRequest
from jarvis_injector.runtime.service import InjectorRuntime


def register_capture_routes(app: FastAPI, runtime: InjectorRuntime) -> None:
    @app.post("/api/capture/last-message")
    def capture_last_message(request: CaptureRequest):
        try:
            return runtime.capture_service.capture_last_message(request).model_dump(mode="json")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

