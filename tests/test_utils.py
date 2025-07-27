import pytest
import responses
from scripts.utils import get_followers, get_following, get_headers, paginate


class TestHeaders:
    """Test cases for header generation."""

    def test_get_headers(self):
        """Test header generation with token."""
        token = "test_token_123"
        headers = get_headers(token)
        
        expected_headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        assert headers == expected_headers

    def test_get_headers_different_token(self):
        """Test header generation with different token."""
        token = "different_token_456"
        headers = get_headers(token)
        
        assert headers["Authorization"] == f"token {token}"
        assert headers["Accept"] == "application/vnd.github.v3+json"


class TestPagination:
    """Test cases for pagination functionality."""

    @responses.activate
    def test_paginate_single_page(self):
        """Test pagination with single page response."""
        mock_data = [{"login": "user1"}, {"login": "user2"}]
        
        responses.add(
            responses.GET,
            "https://api.github.com/test",
            json=mock_data,
            status=200
        )

        result = paginate("https://api.github.com/test", "dummy_token")
        
        assert len(result) == 2
        assert result == mock_data
        assert len(responses.calls) == 1

    @responses.activate
    def test_paginate_multiple_pages(self):
        """Test pagination with multiple pages."""
        page1_data = [{"login": "user1"}, {"login": "user2"}]
        page2_data = [{"login": "user3"}, {"login": "user4"}]
        
        # First page with link to next page
        responses.add(
            responses.GET,
            "https://api.github.com/test",
            json=page1_data,
            status=200,
            headers={"Link": '<https://api.github.com/test?page=2>; rel="next"'}
        )
        
        # Second page without next link
        responses.add(
            responses.GET,
            "https://api.github.com/test?page=2",
            json=page2_data,
            status=200
        )

        result = paginate("https://api.github.com/test", "dummy_token")
        
        assert len(result) == 4
        assert result == page1_data + page2_data
        assert len(responses.calls) == 2

    @responses.activate
    def test_paginate_empty_response(self):
        """Test pagination with empty response."""
        responses.add(
            responses.GET,
            "https://api.github.com/test",
            json=[],
            status=200
        )

        result = paginate("https://api.github.com/test", "dummy_token")
        
        assert len(result) == 0
        assert result == []

    @responses.activate
    def test_paginate_http_error(self):
        """Test pagination with HTTP error."""
        responses.add(
            responses.GET,
            "https://api.github.com/test",
            status=404
        )

        with pytest.raises(Exception):  # requests.HTTPError
            paginate("https://api.github.com/test", "dummy_token")


class TestGetFollowers:
    """Test cases for getting followers."""

    @responses.activate
    def test_get_followers_success(self):
        """Test successfully getting followers."""
        mock_followers = [
            {"login": "follower1", "id": 1},
            {"login": "follower2", "id": 2}
        ]
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/followers",
            json=mock_followers,
            status=200
        )

        result = get_followers("dummy_token")
        
        assert len(result) == 2
        assert result[0]["login"] == "follower1"
        assert result[1]["login"] == "follower2"

    @responses.activate
    def test_get_followers_paginated(self):
        """Test getting followers with pagination."""
        page1 = [{"login": "follower1"}]
        page2 = [{"login": "follower2"}]
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/followers",
            json=page1,
            status=200,
            headers={"Link": '<https://api.github.com/user/followers?page=2>; rel="next"'}
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/followers?page=2",
            json=page2,
            status=200
        )

        result = get_followers("dummy_token")
        
        assert len(result) == 2
        assert result[0]["login"] == "follower1"
        assert result[1]["login"] == "follower2"

    @responses.activate
    def test_get_followers_empty(self):
        """Test getting followers when user has no followers."""
        responses.add(
            responses.GET,
            "https://api.github.com/user/followers",
            json=[],
            status=200
        )

        result = get_followers("dummy_token")
        
        assert len(result) == 0
        assert result == []


class TestGetFollowing:
    """Test cases for getting following list."""

    @responses.activate
    def test_get_following_success(self):
        """Test successfully getting following list."""
        mock_following = [
            {"login": "following1", "id": 1},
            {"login": "following2", "id": 2}
        ]
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/following",
            json=mock_following,
            status=200
        )

        result = get_following("dummy_token")
        
        assert len(result) == 2
        assert result[0]["login"] == "following1"
        assert result[1]["login"] == "following2"

    @responses.activate
    def test_get_following_paginated(self):
        """Test getting following list with pagination."""
        page1 = [{"login": "following1"}]
        page2 = [{"login": "following2"}]
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/following",
            json=page1,
            status=200,
            headers={"Link": '<https://api.github.com/user/following?page=2>; rel="next"'}
        )
        
        responses.add(
            responses.GET,
            "https://api.github.com/user/following?page=2",
            json=page2,
            status=200
        )

        result = get_following("dummy_token")
        
        assert len(result) == 2
        assert result[0]["login"] == "following1"
        assert result[1]["login"] == "following2"

    @responses.activate
    def test_get_following_empty(self):
        """Test getting following list when user follows no one."""
        responses.add(
            responses.GET,
            "https://api.github.com/user/following",
            json=[],
            status=200
        )

        result = get_following("dummy_token")
        
        assert len(result) == 0
        assert result == []