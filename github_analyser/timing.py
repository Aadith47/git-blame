import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from typing import Callable

logger = logging.getLogger(__name__)


class ModelTimeout(TimeoutError):
    """A model took too long, or there was no time left to try it."""


class TimeBudget:
    """A total time allowance for one review, shared by every model that gets tried."""

    def __init__(self, seconds: float, min_useful: float = 1.0, clock: Callable[[], float] = time.monotonic):
        self.seconds = seconds
        self.min_useful = min_useful  # starting a model with less time left than this is pointless
        self._clock = clock
        self._started = clock()

    def remaining(self) -> float:
        return max(0.0, self.seconds - (self._clock() - self._started))

    def has_time(self) -> bool:
        return self.remaining() >= self.min_useful


def run_with_deadline(function: Callable, seconds: float):
    """Runs function() and returns its result, or raises ModelTimeout after `seconds`."""
    pool = ThreadPoolExecutor(max_workers=1)
    future = pool.submit(function)
    try:
        return future.result(timeout=seconds)
    except FutureTimeout:
        if future.done():
            raise
        raise ModelTimeout(f"no answer after {seconds:.0f} seconds") from None
    finally:
        pool.shutdown(wait=False)


def call_with_limits(function: Callable, inputs, name: str, seconds: float, budget: TimeBudget):
    """
    Calls function(inputs) for the model called `name`. It gets at most `seconds`, and never
    more than what is left of the shared budget. With no useful time left, it is skipped.
    """
    if not budget.has_time():
        raise ModelTimeout(f"{name} was skipped: the {budget.seconds:.0f}s time budget is used up")

    allowed = min(seconds, budget.remaining())
    started = time.monotonic()
    try:
        return run_with_deadline(lambda: function(inputs), allowed)
    except Exception as error:
        logger.warning("%s failed after %.1fs: %s: %s", name, time.monotonic() - started,
                       type(error).__name__, error)
        raise