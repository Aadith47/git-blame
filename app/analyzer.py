import pandas as pd


def create_repository_dataframe(repositories):
    repository_data = []

    for repository in repositories:
        repository_data.append({
            "name": repository["name"],
            "stars": repository["stargazers_count"],
            "forks": repository["forks_count"],
            "language": repository["language"] or "Unknown"
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