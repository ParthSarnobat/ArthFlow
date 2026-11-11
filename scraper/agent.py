import asyncio
from playwright.async_api import async_playwright

from .detector import detect_platform
from .schemas import ProductData
from .amazon import scrape_amazon
from .myntra import scrape_myntra
from .meesho import scrape_meesho


SCRAPERS = {
    "amazon": scrape_amazon,
    "myntra": scrape_myntra,
    "meesho": scrape_meesho,
}


async def scraper_agent(url: str, headless: bool = True) -> ProductData:
    """
    Main entry point for the Scraper.
    Pass any Amazon / Myntra / Meesho product URL.
    Returns a ProductData object ready for Image Gen.

    Set headless=False to watch the browser while debugging.
    """
    platform = detect_platform(url)
    scraper_fn = SCRAPERS[platform]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        context = await browser.new_context(
            # Desktop Chrome — all scraper selectors (#productTitle, .pdp-name,
            # etc.) target desktop site HTML, not mobile. Using a mobile UA
            # here caused sites to serve a different layout with different
            # element IDs, which is why selectors were timing out.
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        # Amazon's bot detection actively aborts requests when it sees
        # obvious signs of browser automation (navigator.webdriver=true,
        # missing chrome.runtime, empty plugins list, etc). This patches
        # those tells so the page looks like a normal Chrome browser.
        # Confirmed via debug_connectivity.py: Amazon returned a 202 +
        # empty title on the homepage and ERR_ABORTED on a product page —
        # classic automated-browser fingerprint block, not a code bug.
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters)
            );
        """)

        page = await context.new_page()

        try:
            result = await scraper_fn(page, url)
        finally:
            await browser.close()

    return result


def scrape(url: str, headless: bool = True) -> ProductData:
    """Synchronous wrapper — call this from non-async code."""
    return asyncio.run(scraper_agent(url, headless=headless))