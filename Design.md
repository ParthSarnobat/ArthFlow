# ArthFlow — Design Guide

This covers the visual style for **generated post content** (Agent 2 output)
and the **dashboard UI** (Agent 5). ArthFlow has no public-facing app —
this is just enough design direction to keep output consistent.

## 1. Generated image style (Agent 2)

**Model style**: Faceless or face-obscured (turned away, cropped above the
neck, or angled so features aren't the focus). Reasoning: much easier to
keep visually consistent across generations, avoids uncanny-valley AI-face
issues, and matches what's already working well in this niche (see the
97K-like reference post reviewed earlier).

**Background**: One locked background style, reused across all posts for
brand consistency. Suggested default: clean minimal studio backdrop
(soft neutral tone — beige, warm gray, or off-white) OR a warm indoor
setting with vertical slat paneling (matches the reference screenshot
style). Pick one and lock it in `character_profile.py` — don't vary it
per post.

**Pose variation**: This is the *only* thing that should change between
generations of the same "model" — standing, walking, three-quarter turn,
candid look-away, hands-in-pockets, etc. Keep a rotating list of 5–6 pose
prompts to cycle through.

**Lighting**: Soft, even, diffused studio lighting — no harsh shadows, no
dramatic contrast. Matches commercial/e-commerce photography norms.

**Aspect ratio**:
- Pinterest: 2:3 (vertical, e.g. 1000×1500px) — Pinterest's preferred Pin ratio
- Instagram: 4:5 (vertical, e.g. 1080×1350px) — best feed real estate

## 2. Caption tone

**Pinterest** — descriptive, keyword-rich, SEO-first. Written like a
product description a search engine would reward. Longer (100–200
characters minimum in the title, up to 500 in description).

**Instagram** — short, punchy, conversational. Emoji used sparingly (1–3
per caption). Ends with a clear CTA ("Link in bio 🔗" or similar). Hashtags
placed at the end or in first comment — not scattered mid-caption.

## 3. Brand identity

- Page name: **Arth Essentials**
- Niche: everyday + occasion fashion, Indian market pricing
- Tone: aspirational but accessible — not luxury-only, not budget-only
- No logo/watermark on images for now (keep this simple; revisit if
  brand grows)

## 4. Dashboard UI (Agent 5 — Gradio)

Keep it functional, not fancy — this is a personal tool, not a product.

- **Input tab**: single text box for URL (or multiline for batch), one
  "Generate" button
- **Review tab**: 2-column layout — generated image on the left, product
  info + both captions on the right. Approve / Regenerate / Edit as
  buttons directly below.
- **History tab**: simple table — thumbnail, platform, date posted, status
- No dark mode / theming effort needed — use Gradio's default theme
- Color use, if any: neutral grays with a single accent color (pick
  whatever Gradio's default accent is) — no need to match Arth Essentials'
  brand colors in the internal tool
