from app.github_api import get_user_data, get_user_repositories
from app.analyzer import (
    create_repository_dataframe,
    get_total_stars,
    get_total_forks,
    get_most_starred_repository,
    get_most_used_language,
    get_language_distribution,
    get_repositories_with_descriptions,
    get_repository_count,
    get_active_repositories,
    get_total_open_issues,
    get_total_topics,
    get_description_ratio,
    get_topic_ratio,
    get_active_repository_ratio,
    get_community_score,
    classify_activity,
    classify_documentation,
    classify_discoverability,
    classify_community,
)
from app.scorer import calculate_profile_score
from app.visualizer import plot_language_distribution
from app.ai_analyzer import generate_ai_report


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
    language_distribution = get_language_distribution(repository_df)

    repositories_with_descriptions = get_repositories_with_descriptions(
        repository_df
    )

    repository_count = get_repository_count(repository_df)

    active_repositories = get_active_repositories(
        repository_df
    )

    total_open_issues = get_total_open_issues(
        repository_df
    )

    total_topics = get_total_topics(
        repository_df
    )

    description_ratio = get_description_ratio(repository_df)
    topic_ratio = get_topic_ratio(repository_df)

    active_repository_ratio = get_active_repository_ratio(
        repository_df
    )

    community_score = get_community_score(repository_df)

    activity_strength = classify_activity(
        active_repository_ratio
    )

    documentation_strength = classify_documentation(
        description_ratio
    )

    discoverability_strength = classify_discoverability(
        topic_ratio
    )

    community_strength = classify_community(
        community_score
    )

    profile_score = calculate_profile_score(
        user_data,
        repository_df
    )

    profile_data = {
        "username": user_data["login"],
        "followers": user_data["followers"],
        "following": user_data["following"],
        "repository_count": repository_count,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "most_used_language": most_used_language,
        "languages": list(language_distribution.index),
        "repositories_with_descriptions": repositories_with_descriptions,
        "total_topics": total_topics,
        "active_repositories": active_repositories,
        "profile_score": profile_score,
    }

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

    print("\nLanguage Distribution")
    print("-" * 30)
    print(language_distribution)

    print("\nRepository Quality")
    print("-" * 30)

    print(f"Repositories Analyzed: {repository_count}")
    print(
        f"Repositories With Descriptions: "
        f"{repositories_with_descriptions}"
    )
    print(f"Active Repositories: {active_repositories}")
    print(f"Open Issues: {total_open_issues}")
    print(f"Topics: {total_topics}")

    print("\nRepository Quality Metrics")
    print("-" * 30)

    print(f"Description Coverage: {description_ratio:.0%}")
    print(f"Topic Coverage: {topic_ratio:.0%}")
    print(f"Activity Rate: {active_repository_ratio:.0%}")
    print(f"Community Score: {community_score}")

    print("\nProfile Analysis")
    print("-" * 30)

    print(f"Activity: {activity_strength}")
    print(f"Documentation: {documentation_strength}")
    print(f"Discoverability: {discoverability_strength}")
    print(f"Community: {community_strength}")

    print("\nAI GitHub Report")
    print("-" * 30)

    ai_report = generate_ai_report(profile_data)

    print(ai_report)