import math
from dataclasses import dataclass

from github_analyser.analytics import Facts
from github_analyser.models import Profile

MAX_POINTS = {
    "Profile quality": 15,
    "Repository quality": 25,
    "Documentation": 20,
    "Project diversity": 15,
    "Activity": 15,
    "Community": 10,
}


@dataclass(frozen=True)
class CategoryScore:
    name: str
    points: float
    max_points: int
    parts: dict[str, float]


@dataclass(frozen=True)
class Score:
    total: int
    max_total: int
    categories: list[CategoryScore]


def _share(value: float) -> float:
    """Keeps a number between 0 and 1."""
    return max(0.0, min(1.0, value))


def _log_share(value: float, full_marks_at: float) -> float:
    """0 for nothing, 1 at `full_marks_at`. Early gains count most: 0 to 10 beats 100 to 110."""
    if value <= 0:
        return 0.0
    return _share(math.log1p(value) / math.log1p(full_marks_at))


def _category(name: str, parts: dict[str, float]) -> CategoryScore:
    max_points = MAX_POINTS[name]
    points = min(sum(parts.values()), max_points)
    return CategoryScore(
        name=name,
        points=round(points, 2),
        max_points=max_points,
        parts={part: round(value, 2) for part, value in parts.items()},
    )


def _profile_quality(profile: Profile) -> CategoryScore:
    return _category("Profile quality", {
        "bio": 5 if profile.bio else 0,
        "location or company": 4 if (profile.location or profile.company) else 0,
        "account age (full marks at 1 year)": 6 * _share(profile.account_age_days / 365),
    })


def _repository_quality(facts: Facts) -> CategoryScore:
    third = MAX_POINTS["Repository quality"] / 3
    return _category("Repository quality", {
        "average stars per repo": third * _log_share(facts.avg_stars, 20),
        "topics and license": third * (facts.topics_ratio + facts.license_ratio) / 2,
        "recent pushes and few open issues": third * (facts.active_ratio + facts.healthy_issues_ratio) / 2,
    })


def _documentation(facts: Facts) -> CategoryScore:
    points = MAX_POINTS["Documentation"]
    return _category("Documentation", {
        "README": 0.7 * points * facts.readme_ratio,
        "description": 0.3 * points * facts.description_ratio,
    })


def _project_diversity(facts: Facts) -> CategoryScore:
    known = [language for language in facts.languages if language != "Unknown"]
    return _category("Project diversity", {
        "languages (full marks at 3)": MAX_POINTS["Project diversity"] * min(len(known), 3) / 3,
    })


def _activity(facts: Facts) -> CategoryScore:
    points = MAX_POINTS["Activity"]
    return _category("Activity", {
        "pushed in the last 90 days": 0.4 * points * facts.recent_ratio,
        "pushed in the last year": 0.6 * points * facts.active_ratio,
    })


def _community(profile: Profile, facts: Facts) -> CategoryScore:
    points = MAX_POINTS["Community"]
    return _category("Community", {
        "followers": 0.5 * points * _log_share(profile.followers, 100),
        "stars and forks on own repos": 0.5 * points * _log_share(facts.total_stars + facts.total_forks, 200),
    })


def calculate_score(profile: Profile, facts: Facts) -> Score:
    categories = [
        _profile_quality(profile),
        _repository_quality(facts),
        _documentation(facts),
        _project_diversity(facts),
        _activity(facts),
        _community(profile, facts),
    ]
    return Score(
        total=round(sum(category.points for category in categories)),
        max_total=sum(MAX_POINTS.values()),
        categories=categories,
    )