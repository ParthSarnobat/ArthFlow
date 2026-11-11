import json
import re
from playwright.async_api import Page
from .schemas import ProductData
from .debug_utils import diagnose_failure, safe_goto, is_blocked_page


async def scrape_myntra(page: Page, url: str) -> ProductData:
    """
    Scrape a product page from myntra.com using Playwright.
    Myntra is a React SPA — we wait for the product container to hydrate
    before extracting data. Most data lives in a __NEXT_DATA__ or
    window.__mapp__ JS object; we try that first, then fall back to DOM.
    """

    await page.set_extra_http_headers({
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    })

    try:
        await safe_goto(page, url, wait_until="networkidle", timeout=45000, retries=1)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "myntra", "page_navigation", url)
        raise RuntimeError(diagnosis) from e

    # Wait for the product name to appear (signals React has rendered)
    try:
        await page.wait_for_selector(".pdp-name, h1.pdp-title", timeout=20000)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "myntra", "pdp-name", url)
        raise RuntimeError(diagnosis) from e

    if await is_blocked_page(page):
        diagnosis = await diagnose_failure(page, "myntra", "pdp-name", url)
        raise RuntimeError(diagnosis)

    # ── Try JSON data embedded in the page first ────────────────────────
    product_json = await page.evaluate("""
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
    title_el = page.locator(".pdp-name, h1.pdp-title").first
    if await title_el.count() > 0:
        title = (await title_el.inner_text()).strip()

    # ── Brand ──────────────────────────────────────────────────────────
    brand = ""
    brand_el = page.locator(".pdp-title h1, .brand-name").first
    if await brand_el.count() > 0:
        brand = (await brand_el.inner_text()).strip()

    # ── Price ──────────────────────────────────────────────────────────
    price = ""
    original_price = ""
    discount = ""

    price_el = page.locator(".pdp-price strong, .pdp-mrp strong").first
    if await price_el.count() > 0:
        price = (await price_el.inner_text()).strip()

    mrp_el = page.locator(".pdp-mrp").first
    if await mrp_el.count() > 0:
        original_price = (await mrp_el.inner_text()).strip()

    discount_el = page.locator(".pdp-discount").first
    if await discount_el.count() > 0:
        discount = (await discount_el.inner_text()).strip()

    # ── Rating ─────────────────────────────────────────────────────────
    rating = ""
    rating_el = page.locator(".index-overallRating").first
    if await rating_el.count() > 0:
        rating = (await rating_el.inner_text()).strip()

    # ── Images ─────────────────────────────────────────────────────────
    image_urls = []

    # Myntra loads images into a thumbnail strip
    img_els = await page.locator(".image-grid-col .image-grid-image img, .pdp-image img").all()
    for img in img_els:
        src = await img.get_attribute("src") or ""
        if src.startswith("http") and src not in image_urls:
            # Convert to higher resolution by replacing size in URL
            src = re.sub(r"/h\d+/img", "/h800/img", src)
            image_urls.append(src)

    # ── Colour ─────────────────────────────────────────────────────────
    colour = ""
    colour_el = page.locator(".pdp-color .common-customSelect, .color-title").first
    if await colour_el.count() > 0:
        colour = (await colour_el.inner_text()).strip()
    else:
        # Sometimes colour is in the title itself (e.g. "Blue Kurta")
        colour_match = re.search(
            r'\b(red|blue|green|black|white|pink|yellow|orange|purple|grey|gray|navy|beige|brown|cream|maroon|teal|olive)\b',
            title, re.IGNORECASE
        )
        if colour_match:
            colour = colour_match.group(0).capitalize()

    # ── Fabric / Material ──────────────────────────────────────────────
    fabric = ""
    # Look inside the product details accordion
    detail_items = await page.locator(".pdp-product-description-item, .index-row").all()
    for item in detail_items:
        text = (await item.inner_text()).lower()
        if "fabric" in text or "material" in text:
            fabric = (await item.inner_text()).strip()
            fabric = re.sub(r"fabric|material|:", "", fabric, flags=re.IGNORECASE).strip()
            break

    # ── Description ────────────────────────────────────────────────────
    description = ""
    desc_el = page.locator(".pdp-product-description, .product-desc-info").first
    if await desc_el.count() > 0:
        description = (await desc_el.inner_text()).strip()

    # ── Category / Tags ────────────────────────────────────────────────
    category = ""
    tags = []
    breadcrumb_els = await page.locator(".breadcrumbs-item a").all()
    crumbs = [(await el.inner_text()).strip() for el in breadcrumb_els]
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
        platform="myntra",
        brand=brand,
        rating=rating,
        category=category,
        tags=tags,
    )