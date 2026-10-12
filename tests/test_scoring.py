from dataclasses import replace

import pytest

from github_analyser.analytics import build_analytics
from github_analyser.scoring import MAX_POINTS, _log_share, calculate_score


def test_category_points_add_up_to_100():
    assert sum(MAX_POINTS.values()) == 100


def test_score_stays_between_0_and_100(profile, analytics):
    score = calculate_score(profile, analytics.facts)
    assert 0 <= score.total <= score.max_total == 100


def test_no_category_goes_over_its_maximum(profile, analytics):
    for category in calculate_score(profile, analytics.facts).categories:
        assert 0 <= category.points <= category.max_points


def test_forks_do_not_change_the_score(profile, repos, make_repo):
    big_fork = make_repo(name="big-fork", stars=50_000, forks=9_000, language="Go", is_fork=True)
    without = calculate_score(profile, build_analytics(repos).facts)
    with_fork = calculate_score(profile, build_analytics(repos + [big_fork]).facts)
    assert with_fork == without


def test_more_stars_never_lower_the_score(profile, make_repo):
    low = calculate_score(profile, build_analytics([make_repo(stars=0)]).facts)
    high = calculate_score(profile, build_analytics([make_repo(stars=200)]).facts)
    assert high.total >= low.total


def test_empty_account_scores_zero(profile):
    blank = replace(profile, bio=None, location=None, company=None, followers=0, account_age_days=0)
    assert calculate_score(blank, build_analytics([]).facts).total == 0


def test_profile_quality_full_marks(profile):
    category = calculate_score(profile, build_analytics([]).facts).categories[0]
    assert category.name == "Profile quality"
    assert category.points == 15


@pytest.mark.parametrize(
    "languages, expected",
    [
        ({}, 0),
        ({"Python": 7}, 5),                       # one language still earns a third
        ({"Python": 1, "Rust": 1}, 10),
        ({"Python": 1, "Rust": 1, "Go": 1}, 15),
        ({"Python": 1, "Rust": 1, "Go": 1, "C": 1}, 15),  # more than 3 adds nothing
        ({"Python": 1, "Unknown": 4}, 5),         # "Unknown" is not a language
    ],
)
def test_project_diversity(profile, make_repo, languages, expected):
    facts = replace(build_analytics([make_repo()]).facts, languages=languages)
    diversity = next(c for c in calculate_score(profile, facts).categories if c.name == "Project diversity")
    assert diversity.points == pytest.approx(expected)


def test_log_share_shape():
    assert _log_share(0, 100) == 0
    assert _log_share(10, 100) < _log_share(50, 100) < _log_share(100, 100)
    assert _log_share(10_000, 100) == 1.0
    # early gains count most: 0 -> 10 is worth more than 100 -> 110
    assert _log_share(10, 1000) - _log_share(0, 1000) > _log_share(110, 1000) - _log_share(100, 1000)