from jarvis_injector.core.models import ExecutionPolicy, TargetProfile


DEFAULT_POLICY = ExecutionPolicy()


def resolve_policy(target: TargetProfile) -> ExecutionPolicy:
    return ExecutionPolicy.model_validate(target.policy.model_dump())

