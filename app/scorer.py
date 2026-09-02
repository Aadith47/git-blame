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