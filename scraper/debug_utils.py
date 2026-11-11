import re
from pathlib import Path
from playwright.async_api import Page


DEBUG_DIR = Path(__file__).parent.parent / "debug_snapshots"

# Phrases that indicate the site served a bot-check page instead of the
# real product page — if any of these show up, it's not a broken selector,
# it's bot detection.
BLOCK_INDICATORS = [
    "enter the characters you see",
    "sorry, we just need to make sure",
    "unusual traffic",
    "verify you are a human",
    "captcha",
    "access denied",
    "robot check",
]


async def is_blocked_page(page: Page) -> bool:
    """
    Checks if the current page is a bot-check/access-denied page rather
    than real content. Call this right after a selector "succeeds" too —
    a block page can still contain an <h1> or other element that
    accidentally matches a loose selector, making the scrape look
    successful while actually returning garbage (e.g. title = "Access
    Denied"). Don't rely on exceptions alone to catch this.
    """
    try:
        page_content = await page.content()
    except Exception:
        return False
    page_text_lower = page_content.lower()
    return any(indicator in page_text_lower for indicator in BLOCK_INDICATORS)


async def safe_goto(page: Page, url: str, wait_until: str = "domcontentloaded",
                     timeout: int = 30000, retries: int = 1):
    """
    Navigate with one automatic retry on timeout/network failure.
    Short links (amzn.in, etc.) go through redirect chains that can be
    slower than a direct URL — this gives them a bit more room before
    giving up, and retries once in case of a transient network hiccup.
    """
    last_exc = None
    for attempt in range(retries + 1):
        try:
            await page.goto(url, wait_until=wait_until, timeout=timeout)
            return
        except Exception as e:
            last_exc = e
            if attempt < retries:
                continue
    raise last_exc


async def diagnose_failure(page: Page, platform: str, field: str, url: str) -> str:
    """
    Called when a critical selector (e.g. product title) fails to appear.
    Saves a screenshot + page text for manual inspection, checks for common
    bot-block signatures, and returns a clear diagnostic message.
    """
    DEBUG_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", f"{platform}_{field}")[:80]

    screenshot_path = DEBUG_DIR / f"{safe_name}.png"
    html_path = DEBUG_DIR / f"{safe_name}.html"

    try:
        await page.screenshot(path=str(screenshot_path), full_page=False)
    except Exception:
        screenshot_path = None

    try:
        page_content = await page.content()
        html_path.write_text(page_content, encoding="utf-8")
    except Exception:
        page_content = ""

    page_text_lower = page_content.lower()
    blocked = any(indicator in page_text_lower for indicator in BLOCK_INDICATORS)

    page_title = ""
    try:
        page_title = await page.title()
    except Exception:
        pass

    if blocked:
        reason = (
            f"BOT DETECTION — {platform} served a verification/CAPTCHA page "
            f"instead of the product page."
        )
    else:
        reason = (
            f"SELECTOR NOT FOUND — '{field}' selector did not match anything "
            f"on the page. The site's HTML structure may have changed, or "
            f"the page didn't fully load."
        )

    message = (
        f"\n{'='*60}\n"
        f"SCRAPE FAILED: {platform} — field '{field}'\n"
        f"{'='*60}\n"
        f"URL: {url}\n"
        f"Page title seen by browser: {page_title!r}\n"
        f"Diagnosis: {reason}\n"
    )
    if screenshot_path:
        message += f"Screenshot saved: {screenshot_path}\n"
    if html_path:
        message += f"Full HTML saved: {html_path}\n"
    message += (
        f"\nNext step: open the screenshot above and look at what the "
        f"browser actually saw. If it's a CAPTCHA, re-run with headless=False "
        f"and solve it manually once, or slow down request frequency. If the "
        f"page looks normal, the selector needs updating in {platform}.py.\n"
        f"{'='*60}\n"
    )
    return message