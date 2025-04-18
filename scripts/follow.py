import requests
from utils import get_headers

def follow_users(token, usernames):
    headers = get_headers(token)
    for username in sorted(usernames):
        url = f"https://api.github.com/user/following/{username}"
        resp = requests.put(url, headers=headers)
        if resp.status_code in [204, 304]:
            print(f"✅ Followed: {username}")
        else:
            print(f"❌ Failed to follow {username}: {resp.status_code} - {resp.text}")

def unfollow_users(token, usernames):
    headers = get_headers(token)
    for username in sorted(usernames):
        url = f"https://api.github.com/user/following/{username}"
        resp = requests.delete(url, headers=headers)
        if resp.status_code == 204:
            print(f"🔁 Unfollowed: {username}")
        else:
            print(f"⚠️ Failed to unfollow {username}: {resp.status_code} - {resp.text}")

