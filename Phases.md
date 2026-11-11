# ArthFlow — Build Phases

Each phase should be fully working and testable before moving to the next.
Don't jump ahead — an AI assistant reading this mid-project should pick up
at the first unchecked phase.

## Phase 0 — Project setup ✅
- [x] Folder structure created
- [x] `requirements.txt` with playwright, python-dotenv
- [x] Project renamed to ArthFlow

## Phase 1 — Scraper ✅
- [x] `schemas.py` — ProductData dataclass
- [x] `detector.py` — platform detection from URL
- [x] `amazon.py` — Amazon scraper (Playwright)
- [x] `myntra.py` — Myntra scraper (Playwright)
- [x] `meesho.py` — Meesho scraper (Playwright)
- [x] `agent.py` — main entry point (`scrape(url)`)
- [x] `test_scraper.py` — manual test script
- [ ] **Next action**: run test_scraper.py against a real URL from each
      platform and confirm data quality (images, price, colour, fabric all
      populated correctly). Fix any broken selectors.

## Phase 2 — Image Gen
- [ ] Lock the character profile (model description) in
      `imagegen/character_profile.py`
- [ ] Lock the background profile (studio setting) in the same file
- [ ] Build prompt template combining: character + background + pose +
      outfit description from ProductData
- [ ] Integrate GPT-4o image API call
- [ ] Test: generate 3 images of the same product with different poses,
      visually confirm model + background stay consistent
- [ ] Save generated images locally (or to cloud storage) with a
      predictable naming scheme

## Phase 3 — Caption Writer
- [ ] Build Pinterest caption prompt (SEO-friendly, keyword-rich, longer)
- [ ] Build Instagram caption prompt (punchy, emoji-friendly, CTA to bio link)
- [ ] Generate hashtag sets for both platforms
- [ ] Test against 3–5 sample products, manually review caption quality

## Phase 4 — Dashboard (moved up before publishing agents —
## you need to see output before wiring up real posting)
- [ ] Gradio app: Input tab (paste URL, trigger Scraper → Image Gen →
      Caption Writer)
- [ ] Review tab: show scraped data + generated image + both captions
- [ ] Approve / Regenerate / Edit buttons wired to actual re-runs
- [ ] Test full flow manually: paste URL → review → approve (no posting yet)

## Phase 5 — Pinterest Publisher
- [ ] Set up Pinterest Developer account + OAuth
- [ ] Build `pinterest.py` — create Pin via API v5 (image + title +
      description + affiliate link + board)
- [ ] Wire Approve button in dashboard to actually publish
- [ ] Test: one real pin published end-to-end

## Phase 6 — Instagram Publisher
- [ ] Set up Meta Graph API access (Business/Creator IG account + FB Page)
- [ ] Build `instagram.py` — upload image + caption (no affiliate link in
      caption — link-in-bio only)
- [ ] Wire Approve button in dashboard to actually publish
- [ ] Test: one real Instagram post published end-to-end

## Phase 7 — Storage & history
- [ ] SQLite schema: posts table (product info, image path, captions,
      platform, posted_at, status)
- [ ] Dashboard History tab: list of past posts with status
- [ ] Duplicate-URL detection (warn if a product was already posted)

## Phase 8 — Orchestrator (LangGraph)
- [ ] Wire Agents 1→2→3 as a LangGraph pipeline (replacing direct function
      calls in the dashboard)
- [ ] Add retry logic for scraping failures
- [ ] Add error states that surface cleanly in the dashboard

## Phase 9 — Polish / nice-to-haves (post-MVP)
- [ ] Batch mode — multiple URLs processed as a queue
- [ ] Basic analytics pulled from Pinterest API (saves, clicks)
- [ ] Cost tracking per run (image gen + LLM calls)
- [ ] Amazon Creators API integration once 10+ sales/30 days is hit
      (replaces current Amazon scraper)

---

**Current status: Phase 1 complete, ready to test before starting Phase 2.**
