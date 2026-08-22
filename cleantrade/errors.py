"""CleanTrade API exceptions.

Every error carries the HTTP status code and the server's ``detail``
message so you can react precisely (e.g. 402 -> show an upgrade link).
"""


class CleanTradeError(Exception):
    """Base class for all CleanTrade SDK errors."""

    def __init__(self, message: str, status_code: int | None = None, detail: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class UnauthorizedError(CleanTradeError):
    """HTTP 401 — missing or invalid X-API-Key."""


class LimitReachedError(CleanTradeError):
    """HTTP 402 — monthly order limit of the current plan is reached."""


class NotFoundError(CleanTradeError):
    """HTTP 404 — order not found."""


class ConflictError(CleanTradeError):
    """HTTP 409 — amount busy / no free unique amounts right now."""


class BadRequestError(CleanTradeError):
    """HTTP 400 — invalid request (e.g. unknown plan)."""


def error_from_response(status_code: int, detail: str) -> CleanTradeError:
    """Map an HTTP status to the matching exception type."""
    message = detail or f"CleanTrade API error (HTTP {status_code})"
    if status_code == 400:
        return BadRequestError(message, status_code, detail)
    if status_code == 401:
        return UnauthorizedError(message, status_code, detail)
    if status_code == 402:
        return LimitReachedError(message, status_code, detail)
    if status_code == 404:
        return NotFoundError(message, status_code, detail)
    if status_code == 409:
        return ConflictError(message, status_code, detail)
    return CleanTradeError(message, status_code, detail)
