from fastapi import FastAPI

from jarvis_injector.runtime.service import InjectorRuntime


def register_artifact_routes(app: FastAPI, runtime: InjectorRuntime) -> None:
    @app.get("/api/artifacts/summary")
    def artifact_summary():
        return {
            "targetsDir": str(runtime.config.targets_dir),
            "locatorsDir": str(runtime.config.locators_dir),
            "templatesDir": str(runtime.config.templates_dir),
            "fingerprintsDir": str(runtime.config.fingerprints_dir),
            "motionsDir": str(runtime.config.motions_dir),
            "workflowsDir": str(runtime.config.workflows_dir),
            "executionsLog": str(runtime.config.executions_log_path),
            "screenshotsDir": str(runtime.config.screenshots_dir),
        }

