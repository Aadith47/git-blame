import logging
from datetime import datetime, timezone
from itertools import islice

import requests
from github import Auth, Github
from github.GithubException import (
    BadCredentialsException,
    GithubException,
    RateLimitExceededException,
    UnknownObjectException,
)

from github_analyser.models import Profile, Repo

logger = logging.getLogger(__name__)

MAX_REPOS = 100
README_CHECK_LIMIT = 30


class GitHubAnalyserError(Exception):
    """Any error we can show to the user as plain text."""


class UserNotFoundError(GitHubAnalyserError):
    pass


class InvalidTokenError(GitHubAnalyserError):
    pass


class RateLimitError(GitHubAnalyserError):
    pass


class NetworkError(GitHubAnalyserError):
    pass


def _api_message(error: GithubException) -> str:
    data = error.data if isinstance(error.data, dict) else {}
    return data.get("message", "unknown error")


def _explain(error: Exception, username: str) -> GitHubAnalyserError:
    """Turns whatever PyGithub or requests raised into one of our own readable errors."""
    if isinstance(error, GitHubAnalyserError):
        return error
    if isinstance(error, UnknownObjectException):
        return UserNotFoundError(f"GitHub has no user called '{username}'.")
    if isinstance(error, BadCredentialsException):
        return InvalidTokenError("GitHub rejected your token. Check GITHUB_TOKEN in your .env file.")
    if isinstance(error, RateLimitExceededException):
        return RateLimitError("GitHub rate limit reached. Wait a while and try again.")
    if isinstance(error, GithubException):
        return GitHubAnalyserError(f"GitHub API error {error.status}: {_api_message(error)}")
    if isinstance(error, requests.exceptions.RequestException):
        return NetworkError("Could not reach GitHub. Check your internet connection.")
    return GitHubAnalyserError(f"Unexpected error while reading GitHub: {error}")


def _to_profile(user) -> Profile:
    created = user.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)

    return Profile(
        username=user.login,
        name=user.name,
        bio=user.bio,
        location=user.location,
        company=user.company,
        followers=user.followers,
        following=user.following,
        public_repos=user.public_repos,
        account_age_days=(datetime.now(timezone.utc) - created).days,
        avatar_url=user.avatar_url,
    )


def _to_repo(repo, has_readme: bool | None) -> Repo:
    return Repo(
        name=repo.name,
        description=repo.description,
        stars=repo.stargazers_count,
        forks=repo.forks_count,
        language=repo.language,
        topics=list(repo.topics or []),
        created_at=repo.created_at,
        pushed_at=repo.pushed_at,
        has_readme=has_readme,
        size_kb=repo.size,
        open_issues=repo.open_issues_count,
        license=repo.license.name if repo.license else None,
        is_fork=repo.fork,
    )


def _has_readme(repo) -> bool:
    try:
        repo.get_readme()
        return True
    except UnknownObjectException:
        return False


def fetch_profile_and_repos(token: str, username: str) -> tuple[Profile, list[Repo]]:
    client = Github(auth=Auth.Token(token), per_page=100)
    try:
        user = client.get_user(username)
        profile = _to_profile(user)

        repos = []
        readme_checks = 0
        newest_first = user.get_repos(type="owner", sort="pushed", direction="desc")
        for repo in islice(newest_first, MAX_REPOS):
            has_readme = None
            if not repo.fork and readme_checks < README_CHECK_LIMIT:
                has_readme = _has_readme(repo)
                readme_checks += 1
            repos.append(_to_repo(repo, has_readme))

        return profile, repos
    except Exception as error:
        logger.warning("GitHub request for %r failed: %s", username, error)
        raise _explain(error, username) from error
    finally:
        client.close()