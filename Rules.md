# ArthFlow — Rules for AI-assisted development

These rules apply to any AI (Claude, ChatGPT, Cursor, etc.) working on this
codebase. Read this before making changes.

## Naming convention

Agents are referred to by function, never by number. Use `scraper`,
`imagegen`, `caption_writer`, `publisher`, `dashboard` — not `agent1`,
`agent2`, etc. This applies to folder names, module names, variable
names, and any docs or comments generated for this project.

## Tech stack — stick to this, don't substitute

- **Language**: Python 3.11+ only. No Node/JS backend.
- **Scraping**: Playwright only. Do not suggest BeautifulSoup/requests as
  primary tools — the target sites are JS-rendered and need real browser
  rendering.
- **Orchestration**: LangGraph. Do not introduce CrewAI, AutoGen, or other
  frameworks without discussing it first.
- **Dashboard**: Gradio. Do not switch to Streamlit/Flask/FastAPI+React
  without discussion — Parth already knows Gradio.
- **Database**: Supabase (hosted Postgres). Do not switch to a local
  SQLite file or any other DB — ArthFlow is shared between two people on
  two different devices, so storage must be centrally hosted, not local.
- **Hosting**: Hugging Face Spaces. Do not suggest a different host
  without discussion — Spaces gives free CPU hosting with no card
  required, and works identically for desktop and mobile users.
- **Image generation**: Start with GPT-4o image API. Don't add a second
  image provider unless explicitly asked.

## What the AI should NOT do

- Do not add new pip dependencies without explaining why the existing
  stack can't do it.
- Do not auto-post to Pinterest or Instagram in test/dev code — always
  gate real posting behind an explicit flag or the dashboard's Approve
  button.
- Do not hardcode API keys, tokens, or secrets in any `.py` file — always
  read from `.env` via `python-dotenv`.
- Do not silently swallow errors in scrapers — if a selector fails, raise
  a clear exception naming which field failed to scrape, so debugging is
  fast.
- Do not change the `ProductData` schema (or any agent's data contract)
  without updating `Architecture.md` in the same change.
- Do not remove the human review checkpoint (Agent 5) from the pipeline.

## Error handling expectations

- Every scraper function should fail loudly with a specific error message
  (e.g. `"Failed to extract price for {url} — selector .a-price not found"`),
  not a generic `Exception`.
- Network/timeout errors during scraping should be retried once
  automatically (Playwright timeout → retry with `headless=False` fallback
  is NOT automatic — that's a manual debug step).
- If Agent 2 (image gen) fails or returns an unsafe/blank image, the
  pipeline should stop and flag it in the dashboard — never auto-post a
  failed generation.
- Posting failures (Pinterest/Instagram API errors) must be logged to
  `storage/arthflow.db` with the error message, not just printed to console.

## Code style

- Type hints on all function signatures.
- Dataclasses for structured data (see `schemas.py` pattern) — not raw
  dicts passed between agents.
- Each agent folder is self-contained: one `agent.py` per folder as the
  only import point other agents/orchestrator should use.
- Docstrings on every public function explaining what it does and what
  it returns.

## Cost awareness

- Every call to GPT-4o image gen costs money — do not add automatic
  retries-on-failure for image generation without a hard cap (max 2
  retries per product).
- Log estimated cost per run if easy to do (optional, nice-to-have).

## When in doubt

Ask before:
- Adding a new external API/service
- Changing the folder structure in `Architecture.md`
- Changing what counts as "approved" in the human review step