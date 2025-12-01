import requests


def get_headers(token):
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }


def paginate(url, token):
    headers = get_headers(token)
    results = []
    while url:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        results.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
    return results


def get_followers(token):
    return paginate("https://api.github.com/user/followers", token)


def get_following(token):
    return paginate("https://api.github.com/user/following", token)
