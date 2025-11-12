from urllib.parse import urlparse
from validators.url import url as is_url


def normalize_url(url):
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    return f"{scheme}://{netloc}"


def validate_url(url):
    errors = {}
    if not is_url(url) or len(url) > 255:
        errors["name"] = "Некорректный URL"

    return errors
