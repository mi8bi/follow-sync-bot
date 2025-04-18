import responses
from scripts.utils import get_followers, get_following

import responses
from scripts.utils import get_followers, get_following

MOCK_FOLLOWERS = [
    {"login": "follower1"},
    {"login": "follower2"}
]

MOCK_FOLLOWING = [
    {"login": "follower1"},
    {"login": "not_a_follower"}
]

@responses.activate
def test_get_followers():
    responses.add(
        responses.GET,
        "https://api.github.com/user/followers",
        json=MOCK_FOLLOWERS,
        status=200
    )

    result = get_followers("dummy_token")
    assert len(result) == 2
    assert result[0]["login"] == "follower1"

@responses.activate
def test_get_following():
    responses.add(
        responses.GET,
        "https://api.github.com/user/following",
        json=MOCK_FOLLOWING,
        status=200
    )

    result = get_following("dummy_token")
    assert len(result) == 2
    assert result[1]["login"] == "not_a_follower"

