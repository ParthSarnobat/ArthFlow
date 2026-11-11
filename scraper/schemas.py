from dataclasses import dataclass, field
from typing import List


@dataclass
class ProductData:
    title: str
    price: str
    original_price: str          # before discount, if shown
    discount: str                # e.g. "40% off"
    colour: str
    fabric: str
    description: str
    image_urls: List[str]
    affiliate_link: str          # original URL (your affiliate tag is already in it)
    platform: str                # "amazon" | "myntra" | "meesho"
    brand: str = ""
    rating: str = ""
    category: str = ""
    tags: List[str] = field(default_factory=list)   # extra keywords for caption agent
