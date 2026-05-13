class InjectorError(Exception):
    """Base runtime error."""


class TargetNotFoundError(InjectorError):
    """Raised when a configured target cannot be resolved."""


class ActivationError(InjectorError):
    """Raised when a window cannot be restored or foregrounded."""


class AdapterExecutionError(InjectorError):
    """Raised when an adapter cannot complete its execution path."""


class VerificationError(InjectorError):
    """Raised when verification fails."""

