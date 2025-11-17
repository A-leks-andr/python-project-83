from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class URLCheck:
    url_id: int
    status_code: int
    h1: str
    title: str
    description: str
    created_at: Optional[date] = field(default=None, init=False)
    id: int | None = None


@dataclass
class URL:
    name: str
    created_at: Optional[date] = field(default=None, init=False)
    id: int | None = None
