from datetime import UTC, datetime, timedelta


def expiry(days: int) -> datetime:
    return datetime.now(UTC) + timedelta(days=days)
