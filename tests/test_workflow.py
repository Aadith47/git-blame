import pytest

pytest.importorskip("langgraph")
pytest.importorskip("langchain_core")
pytest.importorskip("langchain_google_genai")
pytest.importorskip("langchain_openai")

from github_analyser.analytics import build_analytics  # noqa: E402
from github_analyser.workflow import route_after_scoring, run_review  # noqa: E402


class ExplodingReviewer:
    def invoke(self, inputs):
        raise AssertionError("the LLM must not be called")


class BrokenReviewer:
    def invoke(self, inputs):
        raise RuntimeError("quota exceeded")


def test_accounts_with_original_repos_go_to_the_review(analytics):
    assert route_after_scoring({"analytics": analytics}) == "review"


def test_accounts_without_original_repos_skip_the_review(make_repo):
    only_forks = build_analytics([make_repo(is_fork=True)])
    assert route_after_scoring({"analytics": only_forks}) == "skip"


def test_full_run_returns_score_review_and_provider(profile, analytics, fake_report, fake_reviewer):
    reviewer = fake_reviewer(fake_report(["cool-api"]), provider="OpenRouter")
    result = run_review(profile, analytics, reviewer)

    assert result["provider"] == "OpenRouter"
    assert result["score"].total > 0
    assert [insight.repo_name for insight in result["report"].project_insights] == ["cool-api"]


def test_no_llm_call_when_there_is_nothing_to_review(profile, make_repo):
    analytics = build_analytics([make_repo(is_fork=True)])
    result = run_review(profile, analytics, ExplodingReviewer())

    assert result["score"].total >= 0
    assert result.get("report") is None
    assert result.get("error") is None


def test_a_failing_llm_gives_a_message_and_keeps_the_score(profile, analytics):
    result = run_review(profile, analytics, BrokenReviewer())

    assert result["report"] is None
    assert "quota exceeded" in result["error"]
    assert result["score"].total > 0