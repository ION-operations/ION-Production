from __future__ import annotations

import argparse
import json

from jarvis_injector.app import build_application
from jarvis_injector.core.enums import Initiator
from jarvis_injector.core.models import DispatchRequest
from jarvis_injector.runtime.service import build_runtime


def main() -> None:
    parser = argparse.ArgumentParser(description="JARVIS injector runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve", help="Start the local API server")
    serve_parser.add_argument("--host", default=None)
    serve_parser.add_argument("--port", type=int, default=None)

    subparsers.add_parser("list-targets", help="List configured targets")

    dispatch_parser = subparsers.add_parser("dispatch", help="Dispatch a command to one target")
    dispatch_parser.add_argument("target_id")
    dispatch_parser.add_argument("command_text")

    args = parser.parse_args()

    if args.command == "serve":
        import uvicorn

        runtime = build_runtime()
        uvicorn.run(
            build_application(),
            host=args.host or runtime.config.api_host,
            port=args.port or runtime.config.api_port,
        )
        return

    runtime = build_runtime()

    if args.command == "list-targets":
        payload = [target.model_dump(mode="json") for target in runtime.target_registry.summaries()]
        print(json.dumps(payload, indent=2))
        return

    if args.command == "dispatch":
        request = DispatchRequest(
            target_id=args.target_id,
            command_text=args.command_text,
            wait_for_completion=False,
            initiated_by=Initiator.CLI,
        )
        result = runtime.dispatch_service.run_now(request)
        print(json.dumps(result.model_dump(mode="json"), indent=2))

