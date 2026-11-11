"""
Quick test for the scraper.
Replace the URL below with any Amazon / Myntra / Meesho product link.
Run with:  python test_scraper.py
"""
import json
from scraper import scrape

# ── Paste your test URL here ───────────────────────────────────────────
TEST_URL = "https://www.meesho.com/sale-price-live-solid-round-neck-cotton-womens-daily-wear-dress-sleeveless-smocked-sundress-boho-ruffle-tiered-swing-a-line-beach-midi-dress-with-pockets/p/7csmvo"

# Set headless=False to see the browser open (useful for debugging)
result = scrape(TEST_URL, headless=False)

print("\n" + "="*60)
print("AGENT 1 OUTPUT")
print("="*60)
print(f"Platform    : {result.platform}")
print(f"Title       : {result.title}")
print(f"Brand       : {result.brand}")
print(f"Price       : {result.price}")
print(f"Original    : {result.original_price}")
print(f"Discount    : {result.discount}")
print(f"Colour      : {result.colour}")
print(f"Fabric      : {result.fabric}")
print(f"Rating      : {result.rating}")
print(f"Category    : {result.category}")
print(f"Tags        : {result.tags}")
print(f"Images ({len(result.image_urls)}):")
for i, img in enumerate(result.image_urls, 1):
    print(f"  {i}. {img}")
print(f"\nDescription :\n{result.description[:300]}...")
print(f"\nAffiliate Link: {result.affiliate_link}")
print("="*60)
