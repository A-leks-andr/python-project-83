from dataclasses import dataclass
from typing import Optional, Tuple

import requests
from bs4 import BeautifulSoup


@dataclass
class Response:
    status_code: int
    content: str


@dataclass
class ErrorResponse:
    error: str
    status_code: Optional[int] = None


def get(url_name: str, logger) -> Optional[Response | ErrorResponse]:
    try:
        resp = requests.get(url_name, timeout=10.0)

        if resp.status_code >= 400:
            logger.warning(
                f"HTTP {resp.status_code} for {url_name}: {resp.reason}"
            )
            return ErrorResponse(
                error=f"HTTP error {resp.status_code}: {resp.reason}",
                status_code=resp.status_code,
            )
        try:
            content_str = resp.content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_str = resp.content.decode("windows=1251")
            except UnicodeDecodeError:
                content_str = resp.content.decode("latin-1")

        return Response(content=content_str, status_code=resp.status_code)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout (10s) exceeded for {url_name}")
        return ErrorResponse(error="Request timeout (10s)")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error for {url_name}: {e}")
        return ErrorResponse(error=f"Connection error: {str(e)}")

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error for {url_name}: {e}")
        return ErrorResponse(error=f"HTTP error: {str(e)}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for {url_name}: {e}")
        return ErrorResponse(error=f"Request failed: {str(e)}")

    except Exception as e:
        logger.critical(f"Unexpected error for {url_name}: {e}", exc_info=True)
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


SEOContent = Tuple[Optional[str], Optional[str], Optional[str]]


def get_seo_content(content: str, logger) -> SEOContent:
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
        logger.error(f"Ошибка при парсинге SEO‑контента: {e}")
        return (None, None, None)
