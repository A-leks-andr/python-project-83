from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class URLCheck:
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    id: int | None = None


@dataclass
class URL:
    name: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    id: int | None = None
