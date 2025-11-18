from urllib.parse import urlparse


def validate(url):
    try:
        result = urlparse(url)
        return (result.scheme in ["http", "https"]) and bool(result.netloc)
    except (AttributeError, TypeError, ValueError):
        return False


def normalize_url(url):
    parsed = urlparse(url)

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]

    return f"{scheme}://{netloc}"
