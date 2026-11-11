import re
from playwright.async_api import Page
from .schemas import ProductData
from .debug_utils import diagnose_failure, safe_goto


async def scrape_amazon(page: Page, url: str) -> ProductData:
    """
    Scrape a product page from amazon.in using Playwright.
    Handles JS-rendered content, bot detection headers, and extracts
    title, price, images, colour, fabric, and description.
    """

    # Set a realistic browser header to reduce bot detection
    await page.set_extra_http_headers({
        "Accept-Language": "en-IN,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    })

    try:
        # 45s timeout + 1 retry — amzn.in short links go through a redirect
        # chain that can be slower than a direct amazon.in URL
        await safe_goto(page, url, wait_until="domcontentloaded", timeout=45000, retries=1)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "amazon", "page_navigation", url)
        raise RuntimeError(diagnosis) from e

    # Wait for the main product title to appear
    try:
        await page.wait_for_selector("#productTitle", timeout=15000)
    except Exception as e:
        diagnosis = await diagnose_failure(page, "amazon", "productTitle", url)
        raise RuntimeError(diagnosis) from e

    # ── Title ──────────────────────────────────────────────────────────
    # Amazon's HTML has TWO elements sharing id="productTitle" — a visible
    # <span> (the real title) and a hidden <input> Amazon uses internally.
    # :visible filters to just the one we actually want.
    title = await page.locator("#productTitle:visible").inner_text()
    title = title.strip()

    # ── Price ──────────────────────────────────────────────────────────
    price = ""
    original_price = ""
    discount = ""

    # Amazon shows price in different selectors depending on the page type
    price_selectors = [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price-whole",
    ]
    for sel in price_selectors:
        el = page.locator(sel).first
        if await el.count() > 0:
            price = (await el.inner_text()).strip()
            break

    # Original (crossed-out) price
    orig_el = page.locator(".a-price.a-text-price .a-offscreen").first
    if await orig_el.count() > 0:
        original_price = (await orig_el.inner_text()).strip()

    # Discount badge
    discount_el = page.locator(".savingsPercentage, #savingsCallout").first
    if await discount_el.count() > 0:
        discount = (await discount_el.inner_text()).strip()

    # ── Brand ──────────────────────────────────────────────────────────
    brand = ""
    brand_el = page.locator("#bylineInfo").first
    if await brand_el.count() > 0:
        brand = (await brand_el.inner_text()).strip().replace("Brand: ", "").replace("Visit the ", "").strip()

    # ── Rating ─────────────────────────────────────────────────────────
    rating = ""
    rating_el = page.locator("#acrPopover").first
    if await rating_el.count() > 0:
        rating = (await rating_el.get_attribute("title") or "").strip()

    # ── Images ─────────────────────────────────────────────────────────
    # Amazon stores all images in a JS variable called 'colorImages'
    image_urls = []
    try:
        raw_js = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script');
                for (const s of scripts) {
                    if (s.textContent.includes("'colorImages'")) {
                        return s.textContent;
                    }
                }
                return null;
            }
        """)
        if raw_js:
            # Extract hi-res image URLs from the JS blob
            matches = re.findall(r'"hiRes":"(https://[^"]+)"', raw_js)
            image_urls = list(dict.fromkeys(matches))  # deduplicate, preserve order
    except Exception:
        pass

    # Fallback: grab from img tags if JS extraction fails
    if not image_urls:
        img_els = await page.locator("#altImages img").all()
        for img in img_els:
            src = await img.get_attribute("src") or ""
            # Convert thumbnail URL to full-size
            full = re.sub(r"\._[A-Z0-9_,]+_\.", ".", src)
            if full.startswith("https://") and full not in image_urls:
                image_urls.append(full)

    # ── Colour ─────────────────────────────────────────────────────────
    colour = ""
    colour_el = page.locator("#variation_color_name .selection").first
    if await colour_el.count() > 0:
        colour = (await colour_el.inner_text()).strip()

    # ── Fabric / Material ──────────────────────────────────────────────
    fabric = ""
    # Amazon shows fabric in the product details table
    detail_rows = await page.locator("#productDetails_techSpec_section_1 tr, #detailBullets_feature_div li").all()
    for row in detail_rows:
        text = (await row.inner_text()).lower()
        if "fabric" in text or "material" in text:
            fabric = (await row.inner_text()).strip()
            fabric = re.sub(r"fabric type|material|:|\n", " ", fabric, flags=re.IGNORECASE).strip()
            break

    # ── Description ────────────────────────────────────────────────────
    description = ""
    desc_el = page.locator("#feature-bullets").first
    if await desc_el.count() > 0:
        description = (await desc_el.inner_text()).strip()

    # ── Category / Tags ────────────────────────────────────────────────
    category = ""
    tags = []
    breadcrumb_els = await page.locator("#wayfinding-breadcrumbs_feature_div a").all()
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
        image_urls=image_urls[:6],   # cap at 6 images
        affiliate_link=url,
        platform="amazon",
        brand=brand,
        rating=rating,
        category=category,
        tags=tags,
    )