import time

import pytest

from github_analyser.timing import ModelTimeout, TimeBudget, call_with_limits, run_with_deadline


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def slow(seconds, value="done"):
    def work(*args):
        time.sleep(seconds)
        return value

    return work


def test_a_fast_call_returns_its_result():
    assert run_with_deadline(lambda: 42, 1) == 42


def test_a_slow_call_is_cut_off_at_the_deadline():
    started = time.monotonic()
    with pytest.raises(ModelTimeout):
        run_with_deadline(slow(0.6), 0.1)
    assert time.monotonic() - started < 0.4  # we did not wait for the slow call to finish


def test_errors_from_the_function_pass_through_unchanged():
    def broken():
        raise ValueError("boom")

    with pytest.raises(ValueError) as error:
        run_with_deadline(broken, 1)
    assert "boom" in str(error.value)


def test_a_timeout_raised_inside_the_function_is_not_mistaken_for_our_deadline():
    def times_out_itself():
        raise TimeoutError("inner")

    with pytest.raises(TimeoutError) as error:
        run_with_deadline(times_out_itself, 1)
    assert not isinstance(error.value, ModelTimeout)
    assert "inner" in str(error.value)


def test_budget_counts_down_and_never_goes_negative():
    clock = FakeClock()
    budget = TimeBudget(20, clock=clock)
    assert budget.remaining() == 20
    clock.now += 5
    assert budget.remaining() == 15
    clock.now += 100
    assert budget.remaining() == 0


def test_a_model_is_not_started_when_too_little_time_is_left():
    clock = FakeClock()
    budget = TimeBudget(10, min_useful=3, clock=clock)
    clock.now += 6
    assert budget.has_time()       # 4 seconds left: worth trying
    clock.now += 2
    assert not budget.has_time()   # 2 seconds left: not worth starting a model


def test_a_model_is_skipped_without_being_called_when_the_budget_is_used_up():
    clock = FakeClock()
    budget = TimeBudget(10, clock=clock)
    clock.now += 10
    calls = []

    with pytest.raises(ModelTimeout) as error:
        call_with_limits(lambda inputs: calls.append(inputs), {"x": 1}, "Backup", 5, budget)

    assert calls == []
    assert "Backup" in str(error.value)


def test_a_model_never_gets_more_time_than_the_budget_has_left():
    budget = TimeBudget(0.15, min_useful=0.01)
    started = time.monotonic()
    with pytest.raises(ModelTimeout):
        call_with_limits(slow(0.6), {}, "Gemini", 5, budget)  # allowed 5s, but only 0.15s are left
    assert time.monotonic() - started < 0.5


def test_models_are_tried_in_order_and_the_last_one_is_skipped_when_time_runs_out():
    budget = TimeBudget(0.3, min_useful=0.05)
    called = []

    def third(inputs):
        called.append("third")
        return "late answer"

    steps = [("first", slow(0.6)), ("second", slow(0.6)), ("third", third)]
    started = time.monotonic()
    results = []
    for name, function in steps:
        try:
            results.append(call_with_limits(function, {}, name, 0.15, budget))
            break
        except ModelTimeout:
            continue

    assert results == []          # nobody answered in time
    assert called == []           # and the third model was never even started
    assert time.monotonic() - started < 0.6