# ArthFlow — Project Requirements Document

## 1. What is this project

ArthFlow is a multi-agent automation system that turns a single product URL
(Amazon / Myntra / Meesho) into a fully published, on-brand social post —
image, caption, and link — on Pinterest and Instagram, for the **Arth
Essentials** fashion affiliate page.

The goal: cut the time from "found a product" to "post is live" from
20–30 minutes of manual work down to a few minutes of review and one click.

## 2. Who is this for

- Primary users: Parth and one friend, both actively posting to Arth
  Essentials — shared access, not public.
- Friend uses mobile most of the time; Parth uses desktop/laptop —
  ArthFlow must work equally well on both (deployed webapp, not a local
  desktop tool).
- Not a public product. No open sign-up. Two-person shared login only.
- Used as a side-business tool alongside a full-time job search — must be
  low-maintenance and not require daily babysitting.

## 3. Problem statement

Manually creating affiliate posts is slow:
- Finding/copying product images from listings looks unoriginal and low-effort
- Photographing real models for every product isn't feasible at this scale
- Writing captions for two different platforms (Pinterest vs Instagram) takes
  time and consistency is hard to maintain
- Manually uploading to two platforms daily doesn't scale as a side hustle

## 4. Goals

- Paste a product URL → get a ready-to-review social post in under 5 minutes
- Keep a **consistent model + background** across all generated images, so
  the page has a recognizable, cohesive aesthetic
- Support multiple affiliate platforms (Amazon now, Myntra/Meesho next)
- Human review step before anything goes live (no fully blind auto-posting)
- Track post history so nothing gets posted twice and performance can be
  reviewed later

## 5. Non-goals (out of scope for now)

- No public multi-tenant / open sign-up support (just the two of you,
  shared login)
- No analytics dashboard beyond basic post history (for now)
- No automatic trend-detection or product discovery (user still finds
  products manually)
- No video/Reel generation in v1 — static images only
- No fully autonomous posting without human approval in v1

## 6. Core features

| # | Feature | Priority |
|---|---------|----------|
| 1 | Paste URL → scrape product data (Amazon, Myntra, Meesho) | Must-have |
| 2 | Generate AI image: consistent model + background, varying pose | Must-have |
| 3 | Generate platform-specific captions (Pinterest + Instagram) | Must-have |
| 4 | Review screen: approve / regenerate / edit before posting | Must-have |
| 5 | Auto-post to Pinterest (via API) | Must-have |
| 6 | Auto-post to Instagram (via API, caption only, no affiliate link in caption) | Must-have |
| 7 | Post history log (avoid duplicate posts, track what's live) | Should-have |
| 8 | Batch mode — paste multiple URLs, review as a queue | Should-have |
| 9 | Retry/error handling if scrape or post fails | Should-have |
| 10 | Basic analytics (likes/saves pulled from Pinterest API) | Nice-to-have |

## 7. Users' definition of "done" for v1

- I can paste one Amazon URL, get a generated faceless-model image + two
  captions (Pinterest, Instagram) in the dashboard, click Approve, and see
  the pin go live on Arth Essentials' Pinterest board — without touching
  code.

## 8. Success metrics

- Time from URL paste to published post < 5 minutes (including review)
- Model/background consistency: images look like they're the same "person"
  across different posts (subjective check by the user, no numeric metric)
- Zero duplicate posts sent to Pinterest/Instagram
- System usable end-to-end without opening a code editor (dashboard only)