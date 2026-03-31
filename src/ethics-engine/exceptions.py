"""Exceptions for Ethics Engine."""


class EthicsEngineException(Exception):
    """Base exception for Ethics Engine."""
    pass


class AuthenticationError(EthicsEngineException):
    """API authentication failed."""
    pass


class RateLimitError(EthicsEngineException):
    """Rate limit exceeded."""
    pass


class TimeoutException(EthicsEngineException):
    """Request timed out."""
    pass


class ModelError(EthicsEngineException):
    """Model inference error."""
    pass


class ValidationError(EthicsEngineException):
    """Request validation error."""
    pass
