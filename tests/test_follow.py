import pytest
import responses

from scripts.follow import follow_users, unfollow_users


class TestFollowUsers:
    """Test cases for following users functionality."""

    @responses.activate
    def test_follow_users_success(self):
        """Test successfully following a user."""
        responses.add(
            responses.PUT, "https://api.github.com/user/following/testuser", status=204
        )

        follow_users("dummy_token", {"testuser"}, dry_run=False)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url.endswith("/following/testuser")
        assert responses.calls[0].request.method == "PUT"

    @responses.activate
    def test_follow_users_already_following(self):
        """Test following a user that is already being followed."""
        responses.add(
            responses.PUT,
            "https://api.github.com/user/following/testuser",
            status=304,  # Not Modified - already following
        )

        follow_users("dummy_token", {"testuser"}, dry_run=False)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.method == "PUT"

    @responses.activate
    def test_follow_users_failure(self):
        """Test handling of failed follow request."""
        responses.add(
            responses.PUT,
            "https://api.github.com/user/following/testuser",
            status=403,
            json={"message": "Forbidden"},
        )

        follow_users("dummy_token", {"testuser"}, dry_run=False)

        assert len(responses.calls) == 1

    def test_follow_users_dry_run(self, capfd):
        """Test follow users in dry run mode."""
        follow_users("dummy_token", {"dryuser"}, dry_run=True)
        out, _ = capfd.readouterr()
        assert "[DRY-RUN] Would follow: dryuser" in out

    def test_follow_users_multiple(self, capfd):
        """Test following multiple users in dry run mode."""
        users = {"user1", "user2", "user3"}
        follow_users("dummy_token", users, dry_run=True)
        out, _ = capfd.readouterr()

        for user in users:
            assert f"[DRY-RUN] Would follow: {user}" in out

    def test_follow_users_empty_list(self):
        """Test following empty list of users."""
        follow_users("dummy_token", set(), dry_run=False)
        # Should not make any requests
        # This test ensures the function handles empty input gracefully


class TestUnfollowUsers:
    """Test cases for unfollowing users functionality."""

    @responses.activate
    def test_unfollow_users_success(self):
        """Test successfully unfollowing a user."""
        responses.add(
            responses.DELETE,
            "https://api.github.com/user/following/testuser",
            status=204,
        )

        unfollow_users("dummy_token", {"testuser"}, dry_run=False)

        assert len(responses.calls) == 1
        assert responses.calls[0].request.url.endswith("/following/testuser")
        assert responses.calls[0].request.method == "DELETE"

    @responses.activate
    def test_unfollow_users_failure(self):
        """Test handling of failed unfollow request."""
        responses.add(
            responses.DELETE,
            "https://api.github.com/user/following/testuser",
            status=404,
            json={"message": "Not Found"},
        )

        unfollow_users("dummy_token", {"testuser"}, dry_run=False)

        assert len(responses.calls) == 1

    def test_unfollow_users_dry_run(self, capfd):
        """Test unfollow users in dry run mode."""
        unfollow_users("dummy_token", {"dryuser"}, dry_run=True)
        out, _ = capfd.readouterr()
        assert "[DRY-RUN] Would unfollow: dryuser" in out

    def test_unfollow_users_multiple(self, capfd):
        """Test unfollowing multiple users in dry run mode."""
        users = {"user1", "user2", "user3"}
        unfollow_users("dummy_token", users, dry_run=True)
        out, _ = capfd.readouterr()

        for user in users:
            assert f"[DRY-RUN] Would unfollow: {user}" in out

    def test_unfollow_users_empty_list(self):
        """Test unfollowing empty list of users."""
        unfollow_users("dummy_token", set(), dry_run=False)
        # Should not make any requests
        # This test ensures the function handles empty input gracefully
