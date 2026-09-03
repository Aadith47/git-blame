import pandas as pd


def get_active_repository_count(repository_df):
    updated_dates = pd.to_datetime(
        repository_df["updated_at"],
        utc=True
    )

    current_date = pd.Timestamp.now(tz="UTC")

    recent_repositories = updated_dates[
        updated_dates >= current_date - pd.Timedelta(days=180)
    ]

    return len(recent_repositories)


def calculate_profile_score(user_data, repository_df):
    score = 0

    repository_count = user_data["public_repos"]
    followers = user_data["followers"]
    stars = repository_df["stars"].sum()
    forks = repository_df["forks"].sum()
    language_count = repository_df["language"].nunique()

    if repository_count >= 10:
        score += 20
    elif repository_count >= 5:
        score += 15
    elif repository_count >= 1:
        score += 10

    if stars >= 100:
        score += 25
    elif stars >= 50:
        score += 20
    elif stars >= 10:
        score += 15
    elif stars > 0:
        score += 10

    if forks >= 50:
        score += 15
    elif forks >= 20:
        score += 12
    elif forks >= 5:
        score += 8
    elif forks > 0:
        score += 5

    if followers >= 100:
        score += 20
    elif followers >= 50:
        score += 15
    elif followers >= 10:
        score += 10
    elif followers > 0:
        score += 5

    if language_count >= 5:
        score += 20
    elif language_count >= 3:
        score += 15
    elif language_count >= 2:
        score += 10
    elif language_count == 1:
        score += 5

    return score


def calculate_profile_score(user_data, repository_df):
    score = 0

    repository_count = user_data["public_repos"]
    followers = user_data["followers"]
    stars = repository_df["stars"].sum()
    forks = repository_df["forks"].sum()
    language_count = repository_df["language"].nunique()

    descriptions = repository_df["description"].notna().sum()
    topics = repository_df["topics"].apply(len).sum()
    active_repositories = get_active_repository_count(repository_df)

    if repository_count >= 10:
        score += 15
    elif repository_count >= 5:
        score += 10
    elif repository_count >= 1:
        score += 5

    if stars >= 100:
        score += 20
    elif stars >= 50:
        score += 15
    elif stars >= 10:
        score += 10
    elif stars > 0:
        score += 5

    if forks >= 50:
        score += 15
    elif forks >= 20:
        score += 10
    elif forks >= 5:
        score += 5

    if followers >= 100:
        score += 15
    elif followers >= 50:
        score += 10
    elif followers >= 10:
        score += 5

    if language_count >= 5:
        score += 10
    elif language_count >= 3:
        score += 7
    elif language_count >= 2:
        score += 5

    if repository_count > 0:
        description_ratio = descriptions / repository_count

        if description_ratio >= 0.8:
            score += 5
        elif description_ratio >= 0.5:
            score += 3

    if topics >= 10:
        score += 3
    elif topics >= 5:
        score += 2

    if active_repositories >= 5:
        score += 2
    elif active_repositories >= 2:
        score += 1

    return min(score, 100)