from datetime import datetime, timedelta, timezone

import pytest

from github_analyser.analytics import build_analytics

NOW = datetime.now(timezone.utc)


def test_forks_do_not_count_toward_any_number(repos, make_repo):
    # Someone forked a huge project. Its stars belong to the upstream author, not to them.
    big_fork = make_repo(name="linux", stars=150_000, forks=50_000, language="C", is_fork=True)
    facts = build_analytics(repos + [big_fork]).facts

    assert facts.total_stars == 33
    assert facts.total_forks == 5
    assert facts.languages == {"Python": 1, "JavaScript": 1, "Rust": 1}
    assert facts.top_repo_name == "cool-api"
    assert (facts.total_repos, facts.original_repos, facts.forked_repos) == (4, 3, 1)


def test_basic_numbers(analytics):
    facts = analytics.facts
    assert facts.avg_stars == pytest.approx(11.0)
    assert facts.top_repo_stars == 25
    assert facts.description_ratio == pytest.approx(2 / 3)
    assert facts.topics_ratio == pytest.approx(2 / 3)
    assert facts.license_ratio == pytest.approx(2 / 3)
    assert facts.readme_ratio == pytest.approx(2 / 3)


def test_missing_language_becomes_unknown(make_repo):
    facts = build_analytics([make_repo(language=None)]).facts
    assert facts.languages == {"Unknown": 1}


def test_readme_ratio_ignores_repos_that_were_never_checked(make_repo):
    repos = [
        make_repo(name="a", has_readme=True),
        make_repo(name="b", has_readme=False),
        make_repo(name="c", has_readme=None),  # not checked: must not count as "missing"
    ]
    facts = build_analytics(repos).facts
    assert facts.readme_ratio == 0.5
    assert facts.readme_checked == 2


def test_activity_uses_last_push(analytics):
    # two repos pushed 10 days ago, one 600 days ago
    assert analytics.facts.recent_ratio == pytest.approx(2 / 3)
    assert analytics.facts.active_ratio == pytest.approx(2 / 3)


def test_a_repo_that_was_never_pushed_counts_from_its_creation_date(make_repo):
    new_but_empty = make_repo(pushed_at=None, created_at=NOW - timedelta(days=5))
    assert build_analytics([new_but_empty]).facts.recent_ratio == 1.0


def test_many_open_issues_count_as_unhealthy(make_repo):
    repos = [make_repo(name="a", open_issues=2), make_repo(name="b", open_issues=500)]
    assert build_analytics(repos).facts.healthy_issues_ratio == 0.5


def test_empty_account_does_not_crash():
    analytics = build_analytics([])
    assert analytics.originals.empty
    assert analytics.facts.original_repos == 0
    assert analytics.facts.languages == {}
    assert analytics.facts.top_repo_name is None


def test_account_with_only_forks_has_no_original_repos(make_repo):
    analytics = build_analytics([make_repo(is_fork=True), make_repo(is_fork=True)])
    assert analytics.facts.original_repos == 0
    assert analytics.facts.forked_repos == 2
    assert analytics.facts.total_stars == 0