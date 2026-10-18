
from datetime import date

import pytest

from github_analyser.limits import DailyLimit, DailyLimitReached


def test_allows_reviews_up_to_the_limit_then_stops():
    budget = DailyLimit(2, today=lambda: date(2026, 10, 1))
    budget.take()
    budget.take()
    with pytest.raises(DailyLimitReached):
        budget.take()


def test_the_budget_resets_on_a_new_day():
    today = {"day": date(2026, 10, 1)}
    budget = DailyLimit(1, today=lambda: today["day"])
    budget.take()
    with pytest.raises(DailyLimitReached):
        budget.take()
    today["day"] = date(2026, 10, 2)
    budget.take()  # a new day, so one review is allowed again


def test_a_limit_of_zero_blocks_every_review():
    budget = DailyLimit(0, today=lambda: date(2026, 10, 1))
    with pytest.raises(DailyLimitReached):
        budget.take()


def test_the_limit_message_is_readable():
    budget = DailyLimit(0, today=lambda: date(2026, 10, 1))
    with pytest.raises(DailyLimitReached) as error:
        budget.take()
    assert "daily AI review limit (0)" in str(error.value)