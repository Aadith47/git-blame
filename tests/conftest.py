"""Shared fixtures and test doubles. Nothing here needs the network or an API key."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from github_analyser.analytics import build_analytics
from github_analyser.models import Profile, Repo

NOW = datetime.now(timezone.utc)


@pytest.fixture
def make_repo():
    """Factory: make_repo(stars=5, is_fork=True) gives a full Repo with sane defaults."""

    def _make(**overrides) -> Repo:
        values = dict(
            name="some-repo",
            description="A repo",
            stars=0,
            forks=0,
            language="Python",
            topics=[],
            created_at=NOW - timedelta(days=400),
            pushed_at=NOW - timedelta(days=10),
            has_readme=True,
            size_kb=100,
            open_issues=0,
            license=None,
            is_fork=False,
        )
        values.update(overrides)
        return Repo(**values)

    return _make


@pytest.fixture
def profile() -> Profile:
    return Profile(
        username="testuser",
        name="Test User",
        bio="Backend developer",
        location="Berlin",
        company=None,
        followers=42,
        following=30,
        public_repos=3,
        account_age_days=900,
        avatar_url="https://example.com/a.png",
    )


@pytest.fixture
def repos(make_repo):
    return [
        make_repo(name="cool-api", stars=25, forks=4, topics=["api"], license="MIT"),
        make_repo(
            name="old-thing",
            description=None,
            language="JavaScript",
            has_readme=False,
            pushed_at=NOW - timedelta(days=600),
        ),
        make_repo(name="rust-toy", stars=8, forks=1, language="Rust", topics=["rust"], license="MIT"),
    ]


@pytest.fixture
def analytics(repos):
    return build_analytics(repos)


class FakeReport:
    """Stands in for GitHubReport. It has only what the code under test touches."""

    def __init__(self, repo_names):
        self.project_insights = [SimpleNamespace(repo_name=name, comment="...") for name in repo_names]

    def model_copy(self, update):
        copy = FakeReport([])
        copy.project_insights = update["project_insights"]
        return copy


class FakeReviewer:
    """Stands in for the LangChain reviewer: has .invoke() and returns (report, provider)."""

    def __init__(self, report, provider="Gemini"):
        self.report = report
        self.provider = provider
        self.seen = None

    def invoke(self, inputs):
        self.seen = inputs
        return self.report, self.provider


@pytest.fixture
def fake_report():
    return FakeReport


@pytest.fixture
def fake_reviewer():
    return FakeReviewer