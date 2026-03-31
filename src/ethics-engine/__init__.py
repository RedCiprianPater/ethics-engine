"""
Ethics Engine - Python SDK

A client library for interacting with the Ethics Engine API.
"""

__version__ = "0.1.0"
__author__ = "NWO Capital"

from .client import EthicsEngine, EthicsEngineAsync
from .schemas import (
    EthicsRequest,
    EthicsResponse,
    ReasoningStep,
    FrameworkMatch,
    ScenarioContext,
)
from .exceptions import (
    EthicsEngineException,
    AuthenticationError,
    RateLimitError,
    TimeoutException,
)

__all__ = [
    "EthicsEngine",
    "EthicsEngineAsync",
    "EthicsRequest",
    "EthicsResponse",
    "ReasoningStep",
    "FrameworkMatch",
    "ScenarioContext",
    "EthicsEngineException",
    "AuthenticationError",
    "RateLimitError",
    "TimeoutException",
]
