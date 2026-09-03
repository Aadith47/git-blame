import requests


def get_user_data(username):
    url = f"https://api.github.com/users/{username}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None


def get_user_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"

    params = {
        "per_page": 100,
        "sort": "updated"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()

    return None
