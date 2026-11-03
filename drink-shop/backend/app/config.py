import os
from datetime import datetime
from zoneinfo import ZoneInfo

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./drink_shop.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "12"))
TZ = ZoneInfo(os.getenv("SHOP_TZ", "Asia/Taipei"))


def now() -> datetime:
    """Shop-local time, stored naive in the database."""
    return datetime.now(TZ).replace(tzinfo=None, microsecond=0)


def months_ago(dt: datetime, months: int) -> datetime:
    """Same day/time `months` months earlier (clamped to month end)."""
    y, m = divmod(dt.year * 12 + (dt.month - 1) - months, 12)
    m += 1
    # clamp day for short months
    import calendar

    day = min(dt.day, calendar.monthrange(y, m)[1])
    return dt.replace(year=y, month=m, day=day)
