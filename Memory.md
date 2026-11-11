# ArthFlow — Memory Log

This file is the **living progress tracker**. Update it at the end of every
work session so a new AI chat (or future you) can pick up instantly without
re-reading the whole codebase.

Paste this file's contents at the start of a new chat along with your
question — that's all the context needed to continue.

---

## Last updated: Phase 1 complete, agents renamed to functional names

## Current state

- Project renamed from generic "affiliate_agent" to **ArthFlow**
- Pinterest page this feeds: **Arth Essentials**
- All 6 planning docs created: PRD.md, Architecture.md, Rules.md,
  Phases.md, Design.md, Memory.md (this file)
- **Naming convention**: agents are called by function, not number —
  `scraper`, `imagegen`, `caption_writer`, `publisher`, `dashboard`.
  `agent1_scraper` folder was renamed to `scraper`, `test_agent1.py`
  renamed to `test_scraper.py`. Apply this convention to all future code.

## What's built and working

- **Scraper** — fully coded, not yet tested against real URLs
  - `scraper/schemas.py` — ProductData dataclass
  - `scraper/detector.py` — platform detection
  - `scraper/amazon.py`, `myntra.py`, `meesho.py` — scrapers
  - `scraper/agent.py` — main entry point, `scrape(url)`
  - `test_scraper.py` — test script, needs a real URL pasted in to run

## Decisions made so far (don't re-litigate these)

- **Amazon**: scraping via Playwright, NOT the official API — Amazon
  retired PA-API v5 (May 15, 2026) and replaced it with the Creators API,
  which requires 10+ qualifying sales in 30 days. Parth doesn't have that
  yet, so scraping is the interim approach. Revisit once sales threshold
  is hit (see Phases.md → Phase 9).
- **Character consistency (Agent 2)**: faceless/face-obscured model,
  locked background, only pose varies. Decided after reviewing a
  reference Instagram post (97K likes, faceless couple model) —
  faceless is both easier to keep consistent AND already proven to work
  in this niche.
- **Human review is mandatory** — no auto-posting without a dashboard
  approval click. This is permanent, not a temporary MVP shortcut.
- **Dashboard**: Gradio, because Parth already used it for a past project
  (AutoBrief Insight) — no learning curve.
- **Instagram captions**: affiliate link goes in bio, never in the
  caption itself (Meta restriction / platform norm).
- **Image storage**: generated images must be hosted on a public URL
  (Cloudinary free tier recommended) — confirmed Instagram's Graph API
  has no local/base64 upload path for photos, it requires `image_url`
  pointing to a publicly accessible server. Pinterest is more flexible
  (accepts base64) but we use the same public-URL approach for both to
  keep one upload step instead of two different paths.
- **Deployment**: ArthFlow is shared by Parth (desktop) and one friend
  (mobile-primary) — not a solo local tool. Deployed as one instance on
  Hugging Face Spaces (free), with Supabase (free Postgres) replacing
  local SQLite for shared, synced storage across devices. Two-user login
  via Gradio's built-in basic auth. All three services (HF Spaces,
  Supabase, Cloudinary) are free at this scale and require no credit
  card — only the OpenAI API (image gen) is a real paid cost.

## Blockers / open questions

- Amazon Creators API access blocked until 10 qualifying sales/30 days —
  scraping is the workaround for now.
- Need to test Scraper against real, current product URLs — selectors
  may break if Amazon/Myntra/Meesho change their DOM structure (this is
  expected to happen periodically; scrapers will need occasional
  maintenance).

## Next action

Run `test_scraper.py` with a real URL from each platform (Amazon, Myntra,
Meesho) and confirm scraped data quality. Fix any broken selectors before
starting Phase 2 (image generation).

---

### How to update this file
After each session, add a short entry below with the date/session topic,
what changed, and what's next. Keep entries brief — this file should stay
scannable, not become a full changelog.