from dataclasses import dataclass
from typing import Optional, Tuple

import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


@dataclass
class Response:
    status_code: int
    content: str


@dataclass
class ErrorResponse:
    error: str
    status_code: Optional[int] = None


def get(url_name):
    try:
        resp = requests.get(url_name, timeout=10)
        resp.raise_for_status()
        return Response(
            content=resp.content.decode('utf-8'),
            status_code=resp.status_code
        )
    except RequestException:
        return None

SEOContent = Tuple[Optional[str], Optional[str], Optional[str]]


def get_seo_content(content: str) -> SEOContent:
    if not content or not isinstance(content, str):
        return (None, None, None)

    try:
        soup = BeautifulSoup(content, "html.parser", from_encoding="utf-8")

        h1_tag = soup.find("h1")
        h1 = h1_tag.get_text(strip=True) if h1_tag else None

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            meta_description = str(meta_desc["content"]).strip()
        else:
            meta_desc = soup.find(
                "meta", attrs={"property": "og:description", "content": True}
            )
            if meta_desc and meta_desc.get("content"):
                meta_description = str(meta_desc["content"]).strip()
            else:
                meta_description = None

        return (h1, title, meta_description)

    except Exception as e:
        print(f"Ошибка при парсинге SEO‑контента: {e}")
        return (None, None, None)
