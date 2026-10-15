class RuntimeErrorBase(Exception):
    """Base class for typed external-integration failures."""


class AuthenticationError(RuntimeErrorBase):
    pass


class RateLimitError(RuntimeErrorBase):
    pass


class ExternalTimeout(RuntimeErrorBase):
    pass


class CanonicalValidationError(RuntimeErrorBase):
    pass
