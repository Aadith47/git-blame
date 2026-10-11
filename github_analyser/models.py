"""The two plain data types that move between modules."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Profile:
    username: str
    name: str | None
    bio: str | None
    location: str | None
    company: str | None
    followers: int
    following: int
    public_repos: int
    account_age_days: int
    avatar_url: str


@dataclass(frozen=True)
class Repo:
    name: str
    description: str | None
    stars: int
    forks: int
    language: str | None
    topics: list[str]
    created_at: datetime
    pushed_at: datetime | None
    has_readme: bool | None  # None means "not checked". It does not mean "missing".
    size_kb: int
    open_issues: int
    license: str | None
    is_fork: bool