from app.github_api import get_user_data, get_user_repositories
from app.analyzer import (
    create_repository_dataframe,
    get_total_stars,
    get_total_forks,
    get_most_starred_repository,
    get_most_used_language,
    get_language_distribution,
)
from app.scorer import calculate_profile_score
from app.visualizer import plot_language_distribution

username = input("Enter GitHub username: ")

user_data = get_user_data(username)
repositories = get_user_repositories(username)

if user_data is None:
    print("GitHub user not found.")
else:
    print("\nGitHub Profile Analyzer")
    print("-" * 30)

    print(f"Username: {user_data['login']}")
    print(f"Name: {user_data['name']}")
    print(f"Followers: {user_data['followers']}")
    print(f"Following: {user_data['following']}")
    print(f"Repositories: {user_data['public_repos']}")

    repository_df = create_repository_dataframe(repositories)

    total_stars = get_total_stars(repository_df)
    total_forks = get_total_forks(repository_df)
    most_starred = get_most_starred_repository(repository_df)
    most_used_language = get_most_used_language(repository_df)

    profile_score = calculate_profile_score(
    user_data,
    repository_df) 

    most_used_language = get_most_used_language(repository_df)
    language_distribution = get_language_distribution(repository_df)

    plot_language_distribution(language_distribution)

    print("\nRepository Data")
    print("-" * 30)
    print(repository_df)

    print("\nRepository Statistics")
    print("-" * 30)

    print(f"Total Stars: {total_stars}")
    print(f"Total Forks: {total_forks}")
    print(f"Most Used Language: {most_used_language}")

    if most_starred is not None:
        print(f"Most Starred Repository: {most_starred['name']}")
        print(f"Stars: {most_starred['stars']}")

    print("\nProfile Score")
    print("-" * 30)
    print(f"Score: {profile_score}/100")

    print("\nProfile Score")
    print("-" * 30)
    print(f"Score: {profile_score}/100")

    print("\nLanguage Distribution")
    print("-" * 30)
    print(language_distribution)

    print(language_distribution)