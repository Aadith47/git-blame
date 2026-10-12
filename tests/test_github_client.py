from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

pytest.importorskip("github")
pytest.importorskip("requests")

import requests  # noqa: E402
from github.GithubException import (  # noqa: E402
    BadCredentialsException,
    GithubException,
    RateLimitExceededException,
    UnknownObjectException,
)

from github_analyser.github_client import (  # noqa: E402
    GitHubAnalyserError,
    InvalidTokenError,
    NetworkError,
    RateLimitError,
    UserNotFoundError,
    _explain,
    _has_readme,
    _to_profile,
    _to_repo,
)

NOW = datetime.now(timezone.utc)


def fake_user(**overrides):
    values = dict(
        login="octo", name="Octo", bio=None, location=None, company=None, followers=3, following=1,
        public_repos=2, created_at=NOW - timedelta(days=100), avatar_url="https://example.com/a.png",
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def fake_repo(**overrides):
    values = dict(
        name="r", description="d", stargazers_count=5, forks_count=1, language="Python", topics=["a"],
        created_at=NOW, pushed_at=NOW, size=10, open_issues_count=2, license=SimpleNamespace(name="MIT"),
        fork=False,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def test_profile_is_mapped_and_age_is_in_days():
    profile = _to_profile(fake_user())
    assert profile.username == "octo"
    assert profile.followers == 3
    assert profile.account_age_days == 100


def test_naive_datetimes_are_treated_as_utc():
    naive = (NOW - timedelta(days=7)).replace(tzinfo=None)
    assert _to_profile(fake_user(created_at=naive)).account_age_days == 7


def test_repo_is_mapped():
    repo = _to_repo(fake_repo(), has_readme=True)
    assert (repo.name, repo.stars, repo.forks, repo.license, repo.is_fork) == ("r", 5, 1, "MIT", False)
    assert repo.topics == ["a"]
    assert repo.has_readme is True


def test_repo_without_license_or_topics():
    repo = _to_repo(fake_repo(license=None, topics=None), has_readme=None)
    assert repo.license is None
    assert repo.topics == []
    assert repo.has_readme is None


def _raises(error):
    def get_readme():
        raise error

    return SimpleNamespace(get_readme=get_readme)


def test_has_readme():
    assert _has_readme(SimpleNamespace(get_readme=lambda: "README")) is True


def test_a_404_means_no_readme():
    assert _has_readme(_raises(UnknownObjectException(404, {"message": "Not Found"}, {}))) is False


def test_other_errors_are_not_mistaken_for_a_missing_readme():
    with pytest.raises(RateLimitExceededException):
        _has_readme(_raises(RateLimitExceededException(403, {"message": "rate limit"}, {})))


def test_unknown_user():
    error = _explain(UnknownObjectException(404, {"message": "Not Found"}, {}), "nobody")
    assert isinstance(error, UserNotFoundError)
    assert "nobody" in str(error)


def test_bad_token():
    assert isinstance(_explain(BadCredentialsException(401, {"message": "Bad credentials"}, {}), "x"), InvalidTokenError)


def test_rate_limit():
    assert isinstance(_explain(RateLimitExceededException(403, {"message": "limit"}, {}), "x"), RateLimitError)


def test_other_api_errors_keep_status_and_message():
    error = _explain(GithubException(500, {"message": "boom"}, {}), "x")
    assert "500" in str(error)
    assert "boom" in str(error)


def test_network_errors():
    assert isinstance(_explain(requests.exceptions.ConnectionError("down"), "x"), NetworkError)


def test_our_own_errors_pass_through_unchanged():
    original = UserNotFoundError("already readable")
    assert _explain(original, "x") is original


def test_anything_else_is_still_wrapped():
    error = _explain(ValueError("oops"), "x")
    assert isinstance(error, GitHubAnalyserError)
    assert "oops" in str(error)