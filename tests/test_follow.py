import responses
from scripts.follow import follow_users, unfollow_users

@responses.activate
def test_follow_users_real():
    responses.add(
        responses.PUT,
        "https://api.github.com/user/following/testuser",
        status=204
    )

    follow_users("dummy_token", {"testuser"}, dry_run=False)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.endswith("/following/testuser")
    assert responses.calls[0].request.method == "PUT"

@responses.activate
def test_unfollow_users_real():
    responses.add(
        responses.DELETE,
        "https://api.github.com/user/following/testuser",
        status=204
    )

    unfollow_users("dummy_token", {"testuser"}, dry_run=False)

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url.endswith("/following/testuser")
    assert responses.calls[0].request.method == "DELETE"

def test_follow_users_dry_run(capfd):
    follow_users("dummy_token", {"dryuser"}, dry_run=True)
    out, _ = capfd.readouterr()
    assert "[DRY-RUN] Would follow: dryuser" in out

def test_unfollow_users_dry_run(capfd):
    unfollow_users("dummy_token", {"dryuser"}, dry_run=True)
    out, _ = capfd.readouterr()
    assert "[DRY-RUN] Would unfollow: dryuser" in out

