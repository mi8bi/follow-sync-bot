import pytest
from datetime import datetime, timezone, timedelta
from scripts.spam import calculate_spam_score, is_spam, _has_suspicious_content, SPAM_THRESHOLD


def make_user(
    name="Test User",
    bio="I write open source code",
    public_repos=10,
    followers=50,
    following=30,
    days_old=365,
):
    """Helper to create a mock GitHub user dict."""
    created_at = (datetime.now(timezone.utc) - timedelta(days=days_old)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    return {
        "login": "testuser",
        "name": name,
        "bio": bio,
        "public_repos": public_repos,
        "followers": followers,
        "following": following,
        "created_at": created_at,
    }


# ---------------------------------------------------------------------------
# _has_suspicious_content
# ---------------------------------------------------------------------------

class TestHasSuspiciousContent:
    def test_empty_string_is_not_suspicious(self):
        assert _has_suspicious_content("") is False

    def test_none_is_not_suspicious(self):
        assert _has_suspicious_content(None) is False

    def test_normal_bio_is_not_suspicious(self):
        assert _has_suspicious_content("I love Python and open source.") is False

    def test_long_random_string_is_suspicious(self):
        assert _has_suspicious_content("aB3kQz9mNpXrTy") is True  # 14 chars, no spaces

    def test_long_numeric_id_is_suspicious(self):
        assert _has_suspicious_content("user123456789") is True

    def test_short_alphanumeric_is_not_suspicious(self):
        # Under 12 chars — could be a normal username/handle
        assert _has_suspicious_content("abc123") is False

    def test_crypto_keyword_is_suspicious(self):
        assert _has_suspicious_content("Follow me for crypto tips!") is True

    def test_nft_keyword_is_suspicious(self):
        assert _has_suspicious_content("NFT artist and collector") is True

    def test_forex_keyword_is_suspicious(self):
        assert _has_suspicious_content("forex trader 🚀") is True

    def test_airdrop_keyword_is_suspicious(self):
        assert _has_suspicious_content("Free airdrop every day") is True

    def test_followback_keyword_is_suspicious(self):
        assert _has_suspicious_content("f4f followback") is True

    def test_earn_money_keyword_is_suspicious(self):
        assert _has_suspicious_content("Learn how to earn money fast") is True

    def test_excessive_emoji_is_suspicious(self):
        assert _has_suspicious_content("🚀🚀🚀🚀 follow me") is True

    def test_three_emoji_is_not_suspicious(self):
        # 3 emoji in a row is acceptable
        assert _has_suspicious_content("🎉🎉🎉 congrats") is False

    def test_shortened_url_is_suspicious(self):
        assert _has_suspicious_content("Check this out: https://bit.ly/abc123") is True

    def test_tinyurl_is_suspicious(self):
        assert _has_suspicious_content("Visit https://tinyurl.com/xyz") is True

    def test_normal_github_url_is_not_suspicious(self):
        assert _has_suspicious_content("See my site: https://example.com") is False


# ---------------------------------------------------------------------------
# calculate_spam_score
# ---------------------------------------------------------------------------

class TestCalculateSpamScore:
    def test_clean_user_has_zero_score(self):
        user = make_user()
        score, reasons = calculate_spam_score(user)
        assert score == 0
        assert reasons == []

    def test_no_name_adds_score(self):
        user = make_user(name=None)
        score, reasons = calculate_spam_score(user)
        assert score >= 1
        assert "no display name" in reasons

    def test_no_bio_adds_score(self):
        user = make_user(bio=None)
        score, reasons = calculate_spam_score(user)
        assert score >= 1
        assert "no bio" in reasons

    def test_no_repos_adds_score(self):
        user = make_user(public_repos=0)
        score, reasons = calculate_spam_score(user)
        assert score >= 2
        assert "no public repositories" in reasons

    def test_very_few_followers_adds_score(self):
        user = make_user(followers=1)
        score, reasons = calculate_spam_score(user)
        assert score >= 1
        assert "very few followers" in reasons

    def test_zero_followers_adds_score(self):
        user = make_user(followers=0)
        score, reasons = calculate_spam_score(user)
        assert "very few followers" in reasons

    def test_two_or_more_followers_not_flagged(self):
        user = make_user(followers=2)
        score, reasons = calculate_spam_score(user)
        assert "very few followers" not in reasons

    def test_new_account_adds_score(self):
        user = make_user(days_old=10)
        score, reasons = calculate_spam_score(user)
        assert score >= 2
        assert any("days old" in r for r in reasons)

    def test_account_29_days_old_is_new(self):
        user = make_user(days_old=29)
        _, reasons = calculate_spam_score(user)
        assert any("days old" in r for r in reasons)

    def test_account_30_days_old_is_not_new(self):
        user = make_user(days_old=30)
        _, reasons = calculate_spam_score(user)
        assert not any("days old" in r for r in reasons)

    def test_suspicious_bio_adds_score(self):
        user = make_user(bio="crypto airdrop free money")
        score, reasons = calculate_spam_score(user)
        assert score >= 2
        assert any("suspicious content" in r for r in reasons)

    def test_suspicious_name_adds_score(self):
        user = make_user(name="aB3kQz9mNpXrTy")
        score, reasons = calculate_spam_score(user)
        assert score >= 2
        assert any("name" in r for r in reasons)

    def test_suspicious_in_both_name_and_bio_scored_once(self):
        user = make_user(name="aB3kQz9mNpXrTy", bio="crypto airdrop")
        score_both, reasons_both = calculate_spam_score(user)
        user_bio_only = make_user(bio="crypto airdrop")
        score_bio, _ = calculate_spam_score(user_bio_only)
        # Scoring should be the same (suspicious_profile counted once)
        suspicious_score_both = sum(
            2 for r in reasons_both if "suspicious content" in r
        )
        assert suspicious_score_both == 2  # only one +2 for suspicious_profile

    def test_multiple_signals_accumulate(self):
        user = make_user(name=None, bio=None, public_repos=0, followers=0, days_old=5)
        score, reasons = calculate_spam_score(user)
        assert score >= SPAM_THRESHOLD
        assert len(reasons) >= 3


# ---------------------------------------------------------------------------
# is_spam
# ---------------------------------------------------------------------------

class TestIsSpam:
    def test_clean_user_is_not_spam(self):
        user = make_user()
        spam, reasons = is_spam(user)
        assert spam is False
        assert reasons == []

    def test_obvious_spam_is_detected(self):
        user = make_user(name=None, bio=None, public_repos=0, followers=0, days_old=5)
        spam, reasons = is_spam(user)
        assert spam is True
        assert len(reasons) > 0

    def test_spam_with_suspicious_bio(self):
        user = make_user(bio="crypto nft airdrop click here", followers=0, public_repos=0)
        spam, _ = is_spam(user)
        assert spam is True

    def test_custom_threshold_lower(self):
        user = make_user(name=None)
        spam, _ = is_spam(user, threshold=1)
        assert spam is True

    def test_custom_threshold_higher(self):
        user = make_user(name=None, bio=None, public_repos=0)
        spam, _ = is_spam(user, threshold=100)
        assert spam is False

    def test_borderline_user_single_signal_not_spam(self):
        # Only bio missing — 1 point, below threshold of 3
        user = make_user(bio=None)
        spam, _ = is_spam(user)
        assert spam is False

    def test_returns_reasons_list_when_spam(self):
        user = make_user(name=None, bio=None, public_repos=0, followers=0, days_old=3)
        spam, reasons = is_spam(user)
        assert spam is True
        assert isinstance(reasons, list)
        assert len(reasons) > 0

    def test_returns_empty_reasons_when_clean(self):
        user = make_user()
        spam, reasons = is_spam(user)
        assert spam is False
        assert reasons == []
