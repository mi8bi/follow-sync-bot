import os
import argparse
from scripts.follow import follow_users, unfollow_users
from scripts.utils import get_followers, get_following, get_user_detail
from scripts.spam import is_spam


def filter_spam_users(token, usernames, label=""):
    """
    Filter out spam accounts from a set of usernames.

    Returns:
        (clean, spam_list): set of non-spam usernames, list of (username, reasons) for spam
    """
    clean = set()
    spam_list = []

    for username in usernames:
        try:
            user_detail = get_user_detail(token, username)
            spam, reasons = is_spam(user_detail)
            if spam:
                spam_list.append((username, reasons))
            else:
                clean.add(username)
        except Exception as e:
            print(f"⚠️  Could not fetch details for {username}{f' ({label})' if label else ''}: {e}")
            # When in doubt, skip rather than follow/unfollow
            clean.add(username)

    return clean, spam_list


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without changing anything")
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

    to_follow_candidates = follower_usernames - following_usernames
    to_unfollow_candidates = following_usernames - follower_usernames

    # Filter spam from new followers before following them
    print("🔍 Checking new followers for spam accounts...")
    to_follow, spam_followers = filter_spam_users(token, to_follow_candidates, label="new follower")
    for username, reasons in spam_followers:
        print(f"🚫 Skipping spam follower: {username} (reasons: {', '.join(reasons)})")

    # Filter spam from existing following list (unfollow spam accounts)
    print("🔍 Checking following list for spam accounts...")
    _, spam_following = filter_spam_users(token, to_unfollow_candidates, label="following")
    spam_following_usernames = {u for u, _ in spam_following}
    for username, reasons in spam_following:
        print(f"🚫 Marking spam account for unfollow: {username} (reasons: {', '.join(reasons)})")

    # Also check mutual follows for spam (users we follow who also follow us)
    mutual = follower_usernames & following_usernames
    print("🔍 Checking mutual follows for spam accounts...")
    _, spam_mutual = filter_spam_users(token, mutual, label="mutual")
    spam_mutual_usernames = {u for u, _ in spam_mutual}
    for username, reasons in spam_mutual:
        print(f"🚫 Marking mutual spam account for unfollow: {username} (reasons: {', '.join(reasons)})")

    to_unfollow = to_unfollow_candidates | spam_following_usernames | spam_mutual_usernames

    follow_users(token, to_follow, dry_run=args.dry_run)
    unfollow_users(token, to_unfollow, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
