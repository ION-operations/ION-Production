from __future__ import annotations

from dataclasses import dataclass

from jarvis_injector import __version__
from jarvis_injector.capture.service import CaptureService
from jarvis_injector.adapters.cdp_adapter import CdpAdapter
from jarvis_injector.adapters.keyboard_adapter import KeyboardAdapter
from jarvis_injector.adapters.manager import AdapterManager
from jarvis_injector.adapters.uia_adapter import UiaAdapter
from jarvis_injector.adapters.visual_adapter import VisualAdapter
from jarvis_injector.config import InjectorConfig
from jarvis_injector.core.dispatcher import DispatchExecutor, DispatchService
from jarvis_injector.core.enums import AdapterKind, Initiator
from jarvis_injector.core.models import DispatchContext, DispatchRequest, HealthStatus, TargetProbeResult
from jarvis_injector.core.policy import resolve_policy
from jarvis_injector.core.queue import ExecutionQueue
from jarvis_injector.core.telemetry import ExecutionTelemetry
from jarvis_injector.memory.vaults import ArtifactVaults
from jarvis_injector.registry.fingerprint_store import FingerprintStore
from jarvis_injector.registry.locator_store import LocatorStore
from jarvis_injector.registry.target_registry import TargetRegistry
from jarvis_injector.registry.template_store import TemplateStore
from jarvis_injector.repair.planner import RepairPlanner
from jarvis_injector.verification.engine import VerificationEngine
from jarvis_injector.windows.input_driver import WindowsInputDriver
from jarvis_injector.windows.window_controller import Win32WindowController


@dataclass
class InjectorRuntime:
    config: InjectorConfig
    target_registry: TargetRegistry
    locator_store: LocatorStore
    template_store: TemplateStore
    fingerprint_store: FingerprintStore
    telemetry: ExecutionTelemetry
    window_controller: Win32WindowController
    adapter_manager: AdapterManager
    verification_engine: VerificationEngine
    repair_planner: RepairPlanner
    capture_service: CaptureService
    queue: ExecutionQueue
    dispatch_service: DispatchService

    def health(self) -> HealthStatus:
        available = {
            AdapterKind.CDP.value: True,
            AdapterKind.UIA.value: True,
            AdapterKind.KEYBOARD.value: True,
            AdapterKind.VISUAL.value: True,
        }
        return HealthStatus(
            status="ok",
            service="jarvis-injector",
            version=__version__,
            queue_depth=self.queue.queue_depth(),
            adapters=available,
        )

    def probe_target(self, target_id: str) -> TargetProbeResult:
        target = self.target_registry.get(target_id)
        if target is None:
            raise KeyError(target_id)

        window = self.window_controller.find_window(target)
        probes = []
        fingerprint = None
        if window is not None:
            fingerprint = self.window_controller.build_fingerprint(target.id, window)
            probe_request = DispatchRequest(
                target_id=target.id,
                command_text="",
                initiated_by=Initiator.CLI,
            )
            probe_ctx = DispatchContext(
                execution_id="probe",
                request=probe_request,
                target=target,
                policy=resolve_policy(target),
                window=window,
            )
            for kind in target.preferred_adapters:
                adapter = self.adapter_manager.adapters.get(kind)
                if adapter is not None:
                    probes.append(adapter.probe(probe_ctx))

        return TargetProbeResult(
            target={
                "id": target.id,
                "display_name": target.display_name,
                "preferred_adapters": target.preferred_adapters,
                "verification_policy": target.verification_policy,
            },
            window=window,
            adapter_probes=probes,
            fingerprint=fingerprint,
        )


def build_runtime() -> InjectorRuntime:
    config = InjectorConfig()
    config.ensure_directories()

    vaults = ArtifactVaults(config)
    target_registry = TargetRegistry(config.targets_dir)
    telemetry = ExecutionTelemetry(config.executions_log_path, config.episodes_db_path)
    window_controller = Win32WindowController()
    input_driver = WindowsInputDriver()

    adapter_manager = AdapterManager(
        {
            AdapterKind.CDP: CdpAdapter(),
            AdapterKind.UIA: UiaAdapter(),
            AdapterKind.KEYBOARD: KeyboardAdapter(input_driver),
            AdapterKind.VISUAL: VisualAdapter(),
        }
    )
    verification_engine = VerificationEngine(window_controller)
    fingerprint_store = FingerprintStore(config.fingerprints_dir, vaults)
    locator_store = LocatorStore(config.locators_dir, vaults)
    template_store = TemplateStore(vaults)
    repair_planner = RepairPlanner()
    capture_service = CaptureService(
        target_registry=target_registry,
        window_controller=window_controller,
    )

    executor = DispatchExecutor(
        target_registry=target_registry,
        window_controller=window_controller,
        adapter_manager=adapter_manager,
        verification_engine=verification_engine,
        fingerprint_store=fingerprint_store,
    )
    queue = ExecutionQueue(executor.execute, telemetry, worker_count=config.worker_count)
    dispatch_service = DispatchService(queue)

    return InjectorRuntime(
        config=config,
        target_registry=target_registry,
        locator_store=locator_store,
        template_store=template_store,
        fingerprint_store=fingerprint_store,
        telemetry=telemetry,
        window_controller=window_controller,
        adapter_manager=adapter_manager,
        verification_engine=verification_engine,
        repair_planner=repair_planner,
        capture_service=capture_service,
        queue=queue,
        dispatch_service=dispatch_service,
    )
