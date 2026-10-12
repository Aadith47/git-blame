import json
from dataclasses import replace

import pytest

pytest.importorskip("langchain_core")
pytest.importorskip("langchain_google_genai")
pytest.importorskip("langchain_openai")

from github_analyser.analytics import build_analytics  # noqa: E402
from github_analyser.llm import build_payload, write_review  # noqa: E402
from github_analyser.scoring import calculate_score  # noqa: E402


def test_payload_cuts_long_free_text(profile, make_repo):
    profile = replace(profile, bio="x" * 1000)
    analytics = build_analytics([make_repo(description="d" * 1000)])
    payload = build_payload(profile, analytics, calculate_score(profile, analytics.facts))
    assert len(payload["profile"]["bio"]) == 300
    assert len(payload["top_repositories"][0]["description"]) == 200


def test_payload_never_contains_forks(profile, make_repo):
    analytics = build_analytics([make_repo(name="mine"), make_repo(name="theirs", stars=9999, is_fork=True)])
    payload = build_payload(profile, analytics, calculate_score(profile, analytics.facts))
    assert [repo["name"] for repo in payload["top_repositories"]] == ["mine"]
    assert payload["repositories"]["total_stars"] == 0


def test_payload_can_be_turned_into_json(profile, analytics):
    payload = build_payload(profile, analytics, calculate_score(profile, analytics.facts))
    assert json.loads(json.dumps(payload))["score"]["out_of"] == 100


def test_insights_about_repos_that_do_not_exist_are_dropped(profile, analytics, fake_report, fake_reviewer):
    reviewer = fake_reviewer(fake_report(["cool-api", "made-up-repo"]))
    report, provider = write_review(reviewer, profile, analytics, calculate_score(profile, analytics.facts))
    assert [insight.repo_name for insight in report.project_insights] == ["cool-api"]
    assert provider == "Gemini"


def test_the_reviewer_receives_the_payload_as_json(profile, analytics, fake_report, fake_reviewer):
    reviewer = fake_reviewer(fake_report([]))
    write_review(reviewer, profile, analytics, calculate_score(profile, analytics.facts))
    assert json.loads(reviewer.seen["data"])["profile"]["username"] == "testuser"