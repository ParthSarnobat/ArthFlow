from urllib.parse import urlparse


PLATFORM_MAP = {
    "amazon.in": "amazon",
    "amzn.in": "amazon",
    "amzn.to": "amazon",
    "myntra.com": "myntra",
    "meesho.com": "meesho",
}


def detect_platform(url: str) -> str:
    """
    Parse the domain from a URL and return the platform name.
    Raises ValueError for unsupported platforms.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")

    for key, platform in PLATFORM_MAP.items():
        if key in domain:
            return platform

    raise ValueError(
        f"Unsupported platform for URL: {url}\n"
        f"Supported: Amazon (amazon.in), Myntra (myntra.com), Meesho (meesho.com)"
    )
