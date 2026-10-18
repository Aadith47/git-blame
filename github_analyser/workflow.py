"""
The LangGraph pipeline:

    START -> scoring -> review -> END
                 \\-> END   (skipped when there is nothing to review)

The branch is the reason to use a graph here: an account with no original repos never
costs an LLM call. Node names must differ from state keys, which is why this is
"scoring" and "review" rather than "score" and "report".
"""

import logging
from typing import TypedDict

from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from github_analyser.analytics import Analytics
from github_analyser.limits import DailyLimitReached
from github_analyser.llm import write_review
from github_analyser.models import Profile
from github_analyser.schemas import GitHubReport
from github_analyser.scoring import Score, calculate_score

logger = logging.getLogger(__name__)


class ReviewState(TypedDict, total=False):
    profile: Profile
    analytics: Analytics
    score: Score
    report: GitHubReport | None
    provider: str | None
    error: str | None


def scoring_node(state: ReviewState) -> dict:
    return {"score": calculate_score(state["profile"], state["analytics"].facts)}


def route_after_scoring(state: ReviewState) -> str:
    return "review" if state["analytics"].facts.original_repos > 0 else "skip"


def make_review_node(reviewer: Runnable):
    def review_node(state: ReviewState) -> dict:
        try:
            report, provider = write_review(reviewer, state["profile"], state["analytics"], state["score"])
            return {"report": report, "provider": provider, "error": None}
        except DailyLimitReached as error:
            # Expected, not a bug, so no traceback in the logs.
            return {"report": None, "provider": None, "error": str(error)}
        except Exception as error:
            # Logged with the traceback, so a real bug in our own code does not
            # hide behind the friendly message the user sees.
            logger.exception("The AI review failed")
            return {"report": None, "provider": None, "error": f"AI review unavailable: {error}"}

    return review_node


def build_graph(reviewer: Runnable):
    graph = StateGraph(ReviewState)
    graph.add_node("scoring", scoring_node)
    graph.add_node("review", make_review_node(reviewer))

    graph.add_edge(START, "scoring")
    graph.add_conditional_edges("scoring", route_after_scoring, {"review": "review", "skip": END})
    graph.add_edge("review", END)
    return graph.compile()


def run_review(profile: Profile, analytics: Analytics, reviewer: Runnable) -> ReviewState:
    return build_graph(reviewer).invoke({"profile": profile, "analytics": analytics})