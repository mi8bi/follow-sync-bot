import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from scripts.main import main


def test_main_normal_execution():
    """Test normal execution of main function."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        # Mock data
        mock_followers = [
            {"login": "follower1"},
            {"login": "follower2"},
            {"login": "mutual_friend"},
        ]
        mock_following = [{"login": "mutual_friend"}, {"login": "not_following_back"}]

        mock_get_followers.return_value = mock_followers
        mock_get_following.return_value = mock_following

        main()

        # Verify API calls were made
        mock_get_followers.assert_called_once_with("test_token")
        mock_get_following.assert_called_once_with("test_token")

        # Verify follow/unfollow calls with expected sets
        mock_follow.assert_called_once_with(
            "test_token", {"follower1", "follower2"}, dry_run=False
        )
        mock_unfollow.assert_called_once_with(
            "test_token", {"not_following_back"}, dry_run=False
        )


def test_main_dry_run_execution():
    """Test main function with dry-run flag."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py", "--dry-run"]),
    ):
        # Mock data
        mock_followers = [{"login": "follower1"}]
        mock_following = [{"login": "following1"}]

        mock_get_followers.return_value = mock_followers
        mock_get_following.return_value = mock_following

        main()

        # Verify dry_run=True was passed
        mock_follow.assert_called_once_with("test_token", {"follower1"}, dry_run=True)
        mock_unfollow.assert_called_once_with(
            "test_token", {"following1"}, dry_run=True
        )


def test_main_missing_token():
    """Test main function when GH_TOKEN is not set."""
    with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", ["main.py"]):
        with pytest.raises(EnvironmentError, match="GH_TOKEN is not set"):
            main()


def test_main_no_changes_needed():
    """Test main function when no follow/unfollow actions are needed."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        # Same users in both lists
        mock_users = [{"login": "user1"}, {"login": "user2"}]

        mock_get_followers.return_value = mock_users
        mock_get_following.return_value = mock_users

        main()

        # Should call functions with empty sets
        mock_follow.assert_called_once_with("test_token", set(), dry_run=False)
        mock_unfollow.assert_called_once_with("test_token", set(), dry_run=False)


def test_main_empty_lists():
    """Test main function with empty followers and following lists."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        mock_get_followers.return_value = []
        mock_get_following.return_value = []

        main()

        # Should call functions with empty sets
        mock_follow.assert_called_once_with("test_token", set(), dry_run=False)
        mock_unfollow.assert_called_once_with("test_token", set(), dry_run=False)


def test_main_api_error_handling():
    """Test main function when API calls raise exceptions."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        mock_get_followers.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            main()


def test_main_with_large_user_lists():
    """Test main function with large user lists to ensure performance."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "test_token"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        # Create large lists
        followers = [{"login": f"follower_{i}"} for i in range(100)]
        following = [{"login": f"following_{i}"} for i in range(50)]

        mock_get_followers.return_value = followers
        mock_get_following.return_value = following

        main()

        # Verify calls were made
        mock_get_followers.assert_called_once()
        mock_get_following.assert_called_once()
        mock_follow.assert_called_once()
        mock_unfollow.assert_called_once()


def test_main_token_from_environment():
    """Test that main function correctly reads token from environment."""
    with (
        patch("scripts.main.get_followers") as mock_get_followers,
        patch("scripts.main.get_following") as mock_get_following,
        patch("scripts.main.follow_users") as mock_follow,
        patch("scripts.main.unfollow_users") as mock_unfollow,
        patch.dict(os.environ, {"GH_TOKEN": "custom_test_token_123"}),
        patch.object(sys, "argv", ["main.py"]),
    ):
        mock_get_followers.return_value = []
        mock_get_following.return_value = []

        main()

        # Verify the correct token was used
        mock_get_followers.assert_called_once_with("custom_test_token_123")
        mock_get_following.assert_called_once_with("custom_test_token_123")
