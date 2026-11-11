import re
from playwright.async_api import Page
from .schemas import ProductData
from .debug_utils import diagnose_failure, safe_goto, is_blocked_page


async def scrape_meesho(page: Page, url: str) -> ProductData:
    """
    Scrape a product page from meesho.com using Playwright.
    Meesho is a Next.js app — we extract from __NEXT_DATA__ where possible
    and fall back to DOM selectors otherwise.
    """

    await page.set_extra_http_headers({
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Upgrade-Insecure-Requests": "1",
    })

    # Meesho uses Akamai Bot Manager, which blocks at the network edge
    # (not a JS challenge — the "Access Denied" page comes from Akamai's
    # servers, not Meesho's app). Akamai weighs browsing behavior, and a
    # request that jumps straight to a deep product URL with no browsing
    # history looks bot-like. Visiting the homepage first, like a real
    # person clicking through, gives a much more normal-looking pattern
    # and lets any Akamai session cookie get set before the real request.
    try:
        await safe_goto(page, "https://www.meesho.com/", wait_until="domcontentloaded", timeout=30000, retries=1)
        await page.wait_for_timeout(2000)  # brief pause, mimics human page-read time
    except Exception:
        pass  # if the warm-up itself fails, still attempt the real URL below —
              # the diagnostic block below will catch it either way

    try:
        await safe_goto(page, url, wait_until="networkidle", timeout=45000, retries=1)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "meesho", "page_navigation", url)
        raise RuntimeError(diagnosis) from e

    # Wait for product title
    try:
        await page.wait_for_selector("h1, .product-title", timeout=20000)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "meesho", "title", url)
        raise RuntimeError(diagnosis) from e

    # This is the exact bug that occurred in testing: Meesho's "Access
    # Denied" block page also has an <h1>, so the wait above succeeds
    # even though it's not a real product page. This check catches that.
    if await is_blocked_page(page):
        diagnosis = await diagnose_failure(page, "meesho", "title", url)
        raise RuntimeError(diagnosis)

    # ── Try __NEXT_DATA__ JSON ──────────────────────────────────────────
    next_data = await page.evaluate("""
        () => {
            try {
                const el = document.getElementById('__NEXT_DATA__');
                if (el) return JSON.parse(el.textContent);
            } catch(e) {}
            return null;
        }
    """)

    # ── Title ──────────────────────────────────────────────────────────
    title = ""

    # Try from JSON first
    if next_data:
        try:
            props = next_data.get("props", {}).get("pageProps", {})
            product = props.get("product", props.get("data", {}))
            title = product.get("name", product.get("title", ""))
        except Exception:
            pass

    if not title:
        title_el = page.locator("h1").first
        if await title_el.count() > 0:
            title = (await title_el.inner_text()).strip()

    # ── Price ──────────────────────────────────────────────────────────
    price = ""
    original_price = ""
    discount = ""

    price_el = page.locator("[class*='price']:not([class*='strike']):not([class*='original'])").first
    if await price_el.count() > 0:
        price = (await price_el.inner_text()).strip()

    strike_el = page.locator("[class*='strike'], [class*='original-price']").first
    if await strike_el.count() > 0:
        original_price = (await strike_el.inner_text()).strip()

    discount_el = page.locator("[class*='discount'], [class*='off']").first
    if await discount_el.count() > 0:
        discount = (await discount_el.inner_text()).strip()

    # ── Brand ──────────────────────────────────────────────────────────
    brand = ""
    brand_el = page.locator("[class*='brand'], [class*='supplier']").first
    if await brand_el.count() > 0:
        brand = (await brand_el.inner_text()).strip()

    # ── Rating ─────────────────────────────────────────────────────────
    rating = ""
    rating_el = page.locator("[class*='rating'] span").first
    if await rating_el.count() > 0:
        rating = (await rating_el.inner_text()).strip()

    # ── Images ─────────────────────────────────────────────────────────
    image_urls = []

    # Meesho shows images in a gallery — grab all product image tags
    img_els = await page.locator("[class*='product'] img, [class*='gallery'] img").all()
    for img in img_els:
        src = await img.get_attribute("src") or ""
        if src.startswith("http") and "product" in src and src not in image_urls:
            image_urls.append(src)

    # Fallback: any image with 'meesho' CDN
    if not image_urls:
        all_imgs = await page.locator("img").all()
        for img in all_imgs:
            src = await img.get_attribute("src") or ""
            if ("meeshocdn" in src or "meesho" in src) and src not in image_urls:
                image_urls.append(src)

    # ── Colour ─────────────────────────────────────────────────────────
    colour = ""
    colour_el = page.locator("[class*='color'] span, [class*='colour'] span").first
    if await colour_el.count() > 0:
        colour = (await colour_el.inner_text()).strip()
    else:
        colour_match = re.search(
            r'\b(red|blue|green|black|white|pink|yellow|orange|purple|grey|gray|navy|beige|brown|cream|maroon|teal|olive)\b',
            title, re.IGNORECASE
        )
        if colour_match:
            colour = colour_match.group(0).capitalize()

    # ── Fabric / Material ──────────────────────────────────────────────
    fabric = ""
    all_text_els = await page.locator("p, span, td, li").all()
    for el in all_text_els:
        text = (await el.inner_text()).lower()
        if "fabric" in text or "material" in text:
            full = (await el.inner_text()).strip()
            if len(full) < 200:   # skip paragraphs; we want short spec lines
                fabric = re.sub(r"fabric|material|:", "", full, flags=re.IGNORECASE).strip()
                break

    # ── Description ────────────────────────────────────────────────────
    description = ""
    desc_el = page.locator("[class*='description'], [class*='details']").first
    if await desc_el.count() > 0:
        description = (await desc_el.inner_text()).strip()

    # ── Category / Tags ────────────────────────────────────────────────
    category = ""
    tags = []
    breadcrumb_els = await page.locator("[class*='breadcrumb'] a").all()
    crumbs = [(await el.inner_text()).strip() for el in breadcrumb_els if await el.inner_text()]
    if crumbs:
        category = crumbs[-1]
        tags = crumbs

    return ProductData(
        title=title,
        price=price,
        original_price=original_price,
        discount=discount,
        colour=colour,
        fabric=fabric,
        description=description,
        image_urls=image_urls[:6],
        affiliate_link=url,
        platform="meesho",
        brand=brand,
        rating=rating,
        category=category,
        tags=tags,
    )