"""
Turns the raw repo list into the facts that everything else uses: the score, the charts
and the AI review. Forks are removed once, here, so no other module has to remember to.
"""

from dataclasses import asdict, dataclass, fields

import pandas as pd

from github_analyser.models import Repo

HEALTHY_OPEN_ISSUES = 20  # more open issues than this looks neglected
RECENT_DAYS = 90
ACTIVE_DAYS = 365


@dataclass(frozen=True)
class Facts:
    total_repos: int
    original_repos: int
    forked_repos: int
    total_stars: int            # own repos only
    total_forks: int            # own repos only
    avg_stars: float
    top_repo_name: str | None
    top_repo_stars: int
    languages: dict[str, int]
    readme_ratio: float         # only repos whose README was actually checked
    readme_checked: int
    description_ratio: float
    topics_ratio: float
    license_ratio: float
    recent_ratio: float         # share of repos pushed to in the last 90 days
    active_ratio: float         # share of repos pushed to in the last 365 days
    healthy_issues_ratio: float


@dataclass
class Analytics:
    facts: Facts
    originals: pd.DataFrame     # one row per own repo, plus a `last_push` column


def _empty_facts(total_repos: int, forked_repos: int) -> Facts:
    return Facts(
        total_repos=total_repos,
        original_repos=0,
        forked_repos=forked_repos,
        total_stars=0,
        total_forks=0,
        avg_stars=0.0,
        top_repo_name=None,
        top_repo_stars=0,
        languages={},
        readme_ratio=0.0,
        readme_checked=0,
        description_ratio=0.0,
        topics_ratio=0.0,
        license_ratio=0.0,
        recent_ratio=0.0,
        active_ratio=0.0,
        healthy_issues_ratio=0.0,
    )


def build_analytics(repos: list[Repo]) -> Analytics:
    columns = [field.name for field in fields(Repo)]
    everything = pd.DataFrame([asdict(repo) for repo in repos], columns=columns)
    originals = everything[~everything["is_fork"].astype(bool)].copy()
    forked = len(everything) - len(originals)

    if originals.empty:
        return Analytics(_empty_facts(len(everything), forked), originals)

    # A repo that was never pushed to (pushed_at is empty) counts from the day it was created.
    now = pd.Timestamp.now(tz="UTC")
    originals["last_push"] = pd.to_datetime(originals["pushed_at"].fillna(originals["created_at"]), utc=True)
    days_idle = (now - originals["last_push"]).dt.days

    readmes_checked = originals["has_readme"].dropna().astype(bool)
    top = originals.loc[originals["stars"].idxmax()]
    languages = originals["language"].fillna("Unknown").value_counts()

    facts = Facts(
        total_repos=len(everything),
        original_repos=len(originals),
        forked_repos=forked,
        total_stars=int(originals["stars"].sum()),
        total_forks=int(originals["forks"].sum()),
        avg_stars=float(originals["stars"].mean()),
        top_repo_name=str(top["name"]),
        top_repo_stars=int(top["stars"]),
        languages={str(name): int(count) for name, count in languages.items()},
        readme_ratio=float(readmes_checked.mean()) if len(readmes_checked) else 0.0,
        readme_checked=len(readmes_checked),
        description_ratio=float(originals["description"].fillna("").str.strip().ne("").mean()),
        topics_ratio=float(originals["topics"].map(len).gt(0).mean()),
        license_ratio=float(originals["license"].notna().mean()),
        recent_ratio=float((days_idle <= RECENT_DAYS).mean()),
        active_ratio=float((days_idle <= ACTIVE_DAYS).mean()),
        healthy_issues_ratio=float((originals["open_issues"] <= HEALTHY_OPEN_ISSUES).mean()),
    )
    return Analytics(facts, originals)