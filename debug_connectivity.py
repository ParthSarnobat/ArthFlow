"""
Connectivity diagnostic — run this BEFORE test_scraper.py to isolate
whether the problem is general internet/Playwright, Amazon specifically,
or the short-link redirect specifically.

Run with:  python debug_connectivity.py
Watch the browser window open — do not run headless for this test.
"""
import asyncio
from playwright.async_api import async_playwright

SHORT_LINK = "https://www.amazon.in/dp/B0FP9L7HZ9?ref=cm_sw_r_cp_ud_dp_J49P48HE5HN7RAA4A5BR&ref_=cm_sw_r_cp_ud_dp_J49P48HE5HN7RAA4A5BR&social_share=cm_sw_r_cp_ud_dp_J49P48HE5HN7RAA4A5BR"   # replace with your actual short link


async def try_nav(page, label, url, wait_until="domcontentloaded", timeout=20000):
    print(f"\n--- Testing: {label} ---")
    print(f"URL: {url}")
    try:
        response = await page.goto(url, wait_until=wait_until, timeout=timeout)
        status = response.status if response else "no response object"
        final_url = page.url
        title = await page.title()
        print(f"✅ SUCCESS — status: {status}")
        print(f"   Final URL after redirects: {final_url}")
        print(f"   Page title: {title!r}")
        return True
    except Exception as e:
        print(f"❌ FAILED — {type(e).__name__}: {e}")
        return False


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)  # watch it happen
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 900},
            locale="en-IN",
        )
        # Same fingerprint patch used in scraper/agent.py — without this,
        # this diagnostic doesn't reflect what the real scraper does.
        # Must be added BEFORE the page is created to apply on first load.
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

        # Test 1: basic internet + Playwright sanity check
        ok1 = await try_nav(page, "Google (sanity check)", "https://www.google.com")

        # Test 2: Amazon base domain (no redirect)
        ok2 = await try_nav(page, "Amazon.in homepage", "https://www.amazon.in")

        # Test 3: the actual short link that failed
        ok3 = await try_nav(
            page, "Short link (amzn.in)", SHORT_LINK,
            wait_until="commit", timeout=30000
        )

        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        print(f"Google loads:        {'YES' if ok1 else 'NO'}")
        print(f"Amazon.in loads:     {'YES' if ok2 else 'NO'}")
        print(f"Short link loads:    {'YES' if ok3 else 'NO'}")

        if not ok1:
            print("\n→ Playwright/internet issue — not specific to Amazon.")
            print("  Check your internet connection, VPN, or firewall/antivirus")
            print("  settings that might block automated browser traffic.")
        elif ok1 and not ok2:
            print("\n→ Amazon is blocking or unreachable specifically.")
            print("  Could be a network-level block, or Amazon flagging this IP.")
        elif ok1 and ok2 and not ok3:
            print("\n→ The short link (amzn.in) is the specific problem.")
            print("  Try expanding it manually in a normal browser first, then")
            print("  use the full amazon.in/dp/... URL instead of the short link.")
        else:
            print("\n→ Everything loaded fine here — the original timeout may")
            print("  have been a one-off. Try test_scraper.py again.")

        input("\nPress Enter to close the browser...")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())