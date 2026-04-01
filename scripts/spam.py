import re
from datetime import datetime, timezone


# Spam score thresholds and weights
SPAM_THRESHOLD = 3

SCORE_WEIGHTS = {
    "no_name": 1,               # Display name not set
    "no_bio": 1,                # Bio not set
    "no_repos": 2,              # Zero public repositories
    "very_few_followers": 1,    # Extremely few followers (< 2)
    "new_account": 2,           # Account created within 30 days
    "suspicious_profile": 2,    # Bio or name contains suspicious patterns
}

# Patterns that suggest spam/bot accounts
_SUSPICIOUS_PATTERNS = [
    # Random-looking strings (long alphanumeric with no spaces, 12+ chars)
    re.compile(r"(?<!\w)[A-Za-z0-9]{12,}(?!\w)"),
    # Sequences of numbers that look like generated IDs
    re.compile(r"\b\d{6,}\b"),
    # Common spam keywords
    re.compile(
        r"\b(crypto|nft|forex|airdrop|investment|profit|earn\s+money|follow\s+back"
        r"|f4f|l4l|followback|gain\s+follow|buy\s+follow"
        r"|OnlyFans|adult\s+content|click\s+here|free\s+money)\b",
        re.IGNORECASE,
    ),
    # Excessive emoji density: 4 or more emoji-like characters in a row
    re.compile(r"[\U0001F300-\U0001FAFF]{4,}"),
    # Suspicious shortened URLs embedded in bio
    re.compile(r"https?://(?:bit\.ly|t\.co|tinyurl\.com|goo\.gl|rb\.gy)/\S+", re.IGNORECASE),
]


def _has_suspicious_content(text: str) -> bool:
    """Return True if the text matches any suspicious pattern."""
    if not text:
        return False
    return any(pattern.search(text) for pattern in _SUSPICIOUS_PATTERNS)


def calculate_spam_score(user: dict) -> tuple[int, list[str]]:
    """
    Calculate a spam score for a GitHub user.

    Args:
        user: GitHub user detail dict (from /users/{username} endpoint)

    Returns:
        (score, reasons): total score and list of reason strings
    """
    score = 0
    reasons = []

    name = user.get("name") or ""
    bio = user.get("bio") or ""

    if not name:
        score += SCORE_WEIGHTS["no_name"]
        reasons.append("no display name")

    if not bio:
        score += SCORE_WEIGHTS["no_bio"]
        reasons.append("no bio")

    if user.get("public_repos", 0) == 0:
        score += SCORE_WEIGHTS["no_repos"]
        reasons.append("no public repositories")

    if user.get("followers", 0) < 2:
        score += SCORE_WEIGHTS["very_few_followers"]
        reasons.append("very few followers")

    created_at = user.get("created_at")
    if created_at:
        created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        days_old = (now - created).days
        if days_old < 30:
            score += SCORE_WEIGHTS["new_account"]
            reasons.append(f"account only {days_old} days old")

    # Check name and bio for suspicious content (scored once even if both match)
    suspicious_fields = []
    if _has_suspicious_content(name):
        suspicious_fields.append("name")
    if _has_suspicious_content(bio):
        suspicious_fields.append("bio")
    if suspicious_fields:
        score += SCORE_WEIGHTS["suspicious_profile"]
        reasons.append(f"suspicious content in {' and '.join(suspicious_fields)}")

    return score, reasons


def is_spam(user: dict, threshold: int = SPAM_THRESHOLD) -> tuple[bool, list[str]]:
    """
    Determine if a GitHub user is likely a spam account.

    Args:
        user: GitHub user detail dict
        threshold: Score threshold above which a user is considered spam

    Returns:
        (is_spam, reasons): bool and list of reason strings
    """
    score, reasons = calculate_spam_score(user)
    return score >= threshold, reasons
