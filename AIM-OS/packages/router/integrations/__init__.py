"""
Router AIM-OS integrations.

Integrates Router with APOE, VIF, SEG, CMC, HHNI, and TCS systems.
"""

from .apoe import APOEIntegration
from .vif import VIFIntegration
from .seg import SEGIntegration
from .cmc import CMCIntegration
from .hhni import HHNIIntegration
from .tcs import TCSIntegration

__all__ = [
    "APOEIntegration",
    "VIFIntegration",
    "SEGIntegration",
    "CMCIntegration",
    "HHNIIntegration",
    "TCSIntegration",
]

