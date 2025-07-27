import pytest
import os
from unittest.mock import patch, MagicMock
from scripts.main import main


class TestMain:
    """Test cases for main script functionality."""

    @patch('scripts.main.get_followers')
    @patch('scripts.main.get_following')
    @patch('scripts.main.follow_users')
    @patch('scripts.main.unfollow_users')
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token'})
    @patch('sys.argv', ['main.py'])
    def test_main_normal_execution(self, mock_unfollow, mock_follow, mock_get_following, mock_get_followers):
        """Test normal execution of main function."""
        # Mock data
        mock_followers = [
            {"login": "follower1"},
            {"login": "follower2"},
            {"login": "mutual_friend"}
        ]
        mock_following = [
            {"login": "mutual_friend"},
            {"login": "not_following_back"}
        ]
        
        mock_get_followers.return_value = mock_followers
        mock_get_following.return_value = mock_following
        
        main()
        
        # Verify API calls were made
        mock_get_followers.assert_called_once_with('test_token')
        mock_get_following.assert_called_once_with('test_token')
        
        # Verify follow/unfollow calls
        mock_follow.assert_called_once_with('test_token', {'follower1', 'follower2'}, dry_run=False)
        mock_unfollow.assert_called_once_with('test_token', {'not_following_back'}, dry_run=False)

    @patch('scripts.main.get_followers')
    @patch('scripts.main.get_following')
    @patch('scripts.main.follow_users')
    @patch('scripts.main.unfollow_users')
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token'})
    @patch('sys.argv', ['main.py', '--dry-run'])
    def test_main_dry_run_execution(self, mock_unfollow, mock_follow, mock_get_following, mock_get_followers):
        """Test main function with dry-run flag."""
        # Mock data
        mock_followers = [{"login": "follower1"}]
        mock_following = [{"login": "following1"}]
        
        mock_get_followers.return_value = mock_followers
        mock_get_following.return_value = mock_following
        
        main()
        
        # Verify dry_run=True was passed
        mock_follow.assert_called_once_with('test_token', {'follower1'}, dry_run=True)
        mock_unfollow.assert_called_once_with('test_token', {'following1'}, dry_run=True)

    @patch.dict(os.environ, {}, clear=True)  # Clear all environment variables
    def test_main_missing_token(self):
        """Test main function when GH_TOKEN is not set."""
        with pytest.raises(EnvironmentError, match="GH_TOKEN is not set"):
            main()

    @patch('scripts.main.get_followers')
    @patch('scripts.main.get_following')
    @patch('scripts.main.follow_users')
    @patch('scripts.main.unfollow_users')
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token'})
    @patch('sys.argv', ['main.py'])
    def test_main_no_changes_needed(self, mock_unfollow, mock_follow, mock_get_following, mock_get_followers):
        """Test main function when no follow/unfollow actions are needed."""
        # Same users in both lists
        mock_users = [
            {"login": "user1"},
            {"login": "user2"}
        ]
        
        mock_get_followers.return_value = mock_users
        mock_get_following.return_value = mock_users
        
        main()
        
        # Should call functions with empty sets
        mock_follow.assert_called_once_with('test_token', set(), dry_run=False)
        mock_unfollow.assert_called_once_with('test_token', set(), dry_run=False)

    @patch('scripts.main.get_followers')
    @patch('scripts.main.get_following')
    @patch('scripts.main.follow_users')
    @patch('scripts.main.unfollow_users')
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token'})
    @patch('sys.argv', ['main.py'])
    def test_main_empty_lists(self, mock_unfollow, mock_follow, mock_get_following, mock_get_followers):
        """Test main function with empty followers and following lists."""
        mock_get_followers.return_value = []
        mock_get_following.return_value = []
        
        main()
        
        # Should call functions with empty sets
        mock_follow.assert_called_once_with('test_token', set(), dry_run=False)
        mock_unfollow.assert_called_once_with('test_token', set(), dry_run=False)

    @patch('scripts.main.get_followers')
    @patch.dict(os.environ, {'GH_TOKEN': 'test_token'})
    @patch('sys.argv', ['main.py'])
    def test_main_api_error_handling(self, mock_get_followers):
        """Test main function when API calls raise exceptions."""
        mock_get_followers.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            main()