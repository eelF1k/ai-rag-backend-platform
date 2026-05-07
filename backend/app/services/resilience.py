from time import monotonic


class AsyncCircuitBreaker:
    def __init__(self, failure_threshold: int = 3, reset_timeout_s: float = 30.0):
        self.failure_threshold = max(1, failure_threshold)
        self.reset_timeout_s = max(1.0, reset_timeout_s)
        self._failures = 0
        self._opened_at: float | None = None

    def allow(self) -> bool:
        if self._opened_at is None:
            return True
        if monotonic() - self._opened_at >= self.reset_timeout_s:
            self._opened_at = None
            self._failures = 0
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._opened_at = monotonic()

