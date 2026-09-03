import pandas as pd


def create_repository_dataframe(repositories):
    repository_data = []

    for repository in repositories:
        repository_data.append({
    "name": repository["name"],
    "description": repository["description"],
    "stars": repository["stargazers_count"],
    "forks": repository["forks_count"],
    "language": repository["language"] or "Unknown",
    "open_issues": repository["open_issues_count"],
    "size": repository["size"],
    "created_at": repository["created_at"],
    "updated_at": repository["updated_at"],
    "topics": repository["topics"]
})

    return pd.DataFrame(repository_data)

def get_total_stars(repository_df):
    return repository_df["stars"].sum()


def get_total_forks(repository_df):
    return repository_df["forks"].sum()


def get_most_starred_repository(repository_df):
    if repository_df.empty:
        return None

    return repository_df.loc[
        repository_df["stars"].idxmax()
    ]


def get_most_used_language(repository_df):
    languages = repository_df["language"]

    if languages.empty:
        return None

    return languages.value_counts().idxmax()

def get_language_distribution(repository_df):
    return repository_df["language"].value_counts()

def get_repositories_with_descriptions(repository_df):
    return repository_df["description"].notna().sum()


def get_repository_count(repository_df):
    return len(repository_df)


def get_active_repositories(repository_df):
    updated_dates = pd.to_datetime(repository_df["updated_at"])
    current_date = pd.Timestamp.now(tz="UTC")

    recent_repositories = updated_dates[
        updated_dates >= current_date - pd.Timedelta(days=180)
    ]

    return len(recent_repositories)


def get_total_open_issues(repository_df):
    return repository_df["open_issues"].sum()


def get_total_topics(repository_df):
    return repository_df["topics"].apply(len).sum()

def get_description_ratio(repository_df):
    if repository_df.empty:
        return 0

    descriptions = repository_df["description"].notna().sum()
    total_repositories = len(repository_df)

    return descriptions / total_repositories


def get_topic_ratio(repository_df):
    if repository_df.empty:
        return 0

    repositories_with_topics = (
        repository_df["topics"].apply(len) > 0
    ).sum()

    total_repositories = len(repository_df)

    return repositories_with_topics / total_repositories


def get_active_repository_ratio(repository_df):
    if repository_df.empty:
        return 0

    updated_dates = pd.to_datetime(
        repository_df["updated_at"],
        utc=True
    )

    current_date = pd.Timestamp.now(tz="UTC")

    active_repositories = (
        updated_dates >= current_date - pd.Timedelta(days=180)
    ).sum()

    return active_repositories / len(repository_df)


def get_community_score(repository_df):
    if repository_df.empty:
        return 0

    stars = repository_df["stars"].sum()
    forks = repository_df["forks"].sum()

    return stars + forks

def classify_activity(activity_ratio):
    if activity_ratio >= 0.75:
        return "Strong"
    elif activity_ratio >= 0.40:
        return "Moderate"
    else:
        return "Weak"


def classify_documentation(description_ratio):
    if description_ratio >= 0.75:
        return "Strong"
    elif description_ratio >= 0.40:
        return "Moderate"
    else:
        return "Weak"


def classify_discoverability(topic_ratio):
    if topic_ratio >= 0.75:
        return "Strong"
    elif topic_ratio >= 0.40:
        return "Moderate"
    else:
        return "Weak"


def classify_community(community_score):
    if community_score >= 100:
        return "Strong"
    elif community_score >= 20:
        return "Moderate"
    else:
        return "Beginner"