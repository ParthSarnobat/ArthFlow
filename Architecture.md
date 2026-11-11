# ArthFlow — Architecture

## 1. High-level flow

```
User pastes URL(s) into dashboard
        │
        ▼
Scraper           (Playwright: Amazon / Myntra / Meesho)
        │
        ▼
Image Gen         (consistent model + background, pose varies)
        │
        ▼
Caption Writer    (separate prompt per platform)
        │
        ▼
Dashboard         (human review: approve / regenerate / edit)
        │
        ├──────────────┐
        ▼              ▼
Pinterest Publisher   Instagram Publisher
        │              │
        ▼              ▼
   Post history log (SQLite)
```

Orchestration across Scraper → Image Gen → Caption Writer → Publishers is
handled by **LangGraph**. Dashboard is the entry and exit point — it
triggers the graph and displays/collects human input at the review
checkpoint.

**Naming convention**: agents are referred to by function, not by number
(`scraper`, not `agent1`). Folder and module names follow the same
pattern — see folder structure below.

## 2. Folder structure

```
arthflow/
│
├── PRD.md
├── Architecture.md
├── Rules.md
├── Phases.md
├── Design.md
├── Memory.md
│
├── requirements.txt
├── .env                          # API keys (never committed)
├── .env.example
├── main.py                       # launches the dashboard
│
├── scraper/
│   ├── __init__.py
│   ├── agent.py                  # entry point: scrape(url)
│   ├── schemas.py                # ProductData dataclass
│   ├── detector.py               # platform detection
│   ├── amazon.py
│   ├── myntra.py
│   └── meesho.py
│
├── imagegen/
│   ├── __init__.py
│   ├── agent.py                  # entry point: generate_image(product, pose)
│   ├── character_profile.py      # locked model + background description
│   └── prompts.py
│
├── caption_writer/
│   ├── __init__.py
│   ├── agent.py                  # entry point: generate_captions(product)
│   ├── pinterest_prompt.py
│   └── instagram_prompt.py
│
├── publisher/
│   ├── __init__.py
│   ├── pinterest.py               # Pinterest API v5 posting
│   └── instagram.py               # Meta Graph API posting
│
├── dashboard/
│   ├── __init__.py
│   └── app.py                     # Gradio dashboard (review, approve, post)
│
├── orchestrator/
│   ├── __init__.py
│   └── graph.py                   # LangGraph pipeline definition
│
├── storage/
│   ├── __init__.py
│   └── db.py                      # Supabase client setup + queries
│
└── tests/
    ├── test_scraper.py
    ├── test_imagegen.py
    ├── test_caption_writer.py
    └── test_publisher.py
```

## 3. Tech stack

| Layer | Choice | Why |
|---|---|---|
| Orchestration | LangGraph | Free, handles branching (Pinterest vs Instagram), good retry/error support |
| Scraping | Playwright (Python) | Handles JS-heavy sites (Myntra, Meesho), one tool for all 3 platforms |
| Image generation | GPT-4o image gen (start) → Flux/LoRA on RunPod (later, if cost matters) | Fastest to get working; character consistency via locked prompt |
| Caption generation | GPT-4o or Claude | Cheap, fast, good at tone-matching per platform |
| Dashboard | Gradio | Parth already knows it from AutoBrief Insight; fast to build |
| Hosting | Hugging Face Spaces (free CPU) | Deployed once, works from any device (desktop + mobile) for both users, no card needed |
| Database | Supabase (free Postgres) | Shared, hosted — both users read/write the same live data, no sync conflicts. No card needed |
| Image hosting | Cloudinary (free tier) | Instagram Graph API requires a public image URL — no local upload path exists. No card needed |
| Pinterest posting | Pinterest API v5 | Official, free, supports Pin creation with image + link |
| Instagram posting | Meta Graph API | Official, free, requires Business/Creator IG account |

## 4. Data contracts between agents

**Scraper → Image Gen**: `ProductData` (see `scraper/schemas.py`)
- title, price, colour, fabric, image_urls, affiliate_link, platform

**Image Gen → Caption Writer**: `GeneratedImage`
- image_path (local or hosted URL), pose_variant, product_ref (ProductData)

**Caption Writer → Dashboard**: `CaptionSet`
- pinterest_caption, pinterest_title, instagram_caption, hashtags[]

**Dashboard → Pinterest/Instagram Publisher**: `ApprovedPost`
- image_path, caption, board_id (Pinterest) / nothing extra (Instagram),
  affiliate_link, approved_at timestamp

## 5. Character & background consistency (Image Gen core mechanism)

- A single locked "character profile" (text description) lives in
  `imagegen/character_profile.py` — reused in every image prompt.
- A single locked "background profile" (studio backdrop, described in
  text) also lives there.
- Only the **pose** and **product/outfit description** change per call.
- This keeps Image Gen's prompt construction simple: fixed description +
  fixed background + variable pose + variable outfit.

## 6. Human-in-the-loop checkpoint

Dashboard is a mandatory checkpoint — no image auto-publishes without a
human clicking Approve. This is a deliberate design choice, not a missing
feature — see PRD non-goals.

## 7. Deployment & storage architecture

**Hosting — Hugging Face Spaces (free)**
ArthFlow runs as one deployed instance, not a local script. Both Parth
(desktop) and friend (mobile-primary) hit the same URL. Free CPU Basic
tier is sufficient — no GPU needed since image generation calls out to
GPT-4o's API rather than running locally. No credit card required for
this tier.

**Access — simple two-user login**
Since this is shared between two specific people (not public), the
dashboard uses Gradio's built-in basic auth with two username/password
pairs. No need for a full auth system at this scale.

**Structured data (product info, captions, post status/history)**
→ Supabase (free Postgres), not local SQLite. Reason: two people on two
different devices need to see the same live data — a local SQLite file
can't be safely shared/synced across machines. Free tier gives 500MB
storage (plenty at this scale) and requires no card. Note: free projects
auto-pause after 7 days of no activity — resuming takes ~30 seconds from
the Supabase dashboard, no data is lost.

**Generated image files**
→ Must be hosted on a **publicly accessible URL**, not local disk.
  Reason: Instagram's Graph API requires `image_url` to point to a public
  server — Meta's servers fetch the image themselves at publish time, and
  there is no local/base64 upload path for photos. Pinterest's API v5 is
  more flexible and accepts base64 image data directly, but since one
  generated image needs to serve both platforms, the public-URL path is
  used for both to keep the pipeline simple.

Recommended: **Cloudinary free tier** (25 credits/month, no card needed)
— simple Python SDK, handles format/resize conversion (useful since
Instagram requires JPEG only, specific aspect ratios).

Flow: Image Gen generates image → uploads to Cloudinary → gets back a
public URL → URL stored in Supabase alongside the rest of the post row →
both `publisher/pinterest.py` and `publisher/instagram.py` use that same
URL.

**Cost note**: Hugging Face Spaces, Supabase, and Cloudinary are all free
at ArthFlow's scale and require no credit card. The one real cost is the
OpenAI API (GPT-4o image generation), which is pay-as-you-go from the
start.