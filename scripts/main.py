import argparse
import os

from scripts.follow import follow_users, unfollow_users
from scripts.utils import get_followers, get_following


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without changing anything",
    )
    args = parser.parse_args()

    token = os.getenv("GH_TOKEN")
    if not token:
        raise EnvironmentError("GH_TOKEN is not set")

    print("🔄 Fetching followers...")
    followers = get_followers(token)

    print("🔄 Fetching following...")
    following = get_following(token)

    follower_usernames = set(f["login"] for f in followers)
    following_usernames = set(f["login"] for f in following)

    to_follow = follower_usernames - following_usernames
    to_unfollow = following_usernames - follower_usernames

    follow_users(token, to_follow, dry_run=args.dry_run)
    unfollow_users(token, to_unfollow, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
