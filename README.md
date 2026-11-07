# Beach, Please! — automated Instagram posts

Posts 3x/day, driven by your app's real data:

- **08:00 SAST** — top-scoring **beach** of the day (punchy copy)
- **12:00 SAST** — top-scoring **tidal pool** of the day (punchy copy)
- **19:00 SAST** — a Cape Town beach fact, or (1 in 3 evenings) a fact about
  how the app itself works

Cost: **R0/month**. Runs on GitHub Actions' free tier (well under its
2,000 free minutes/month even on a private repo — this repo is public
anyway, which is unlimited); posts via Instagram's own Graph API, which is
free for posting to your own account.

## How it decides what's "best today"

`beach_data.py` is a direct port of your app's real `BeachScoring.swift` —
same 23 beaches/pools, same scoring formula (wind shelter, blue flag, tide
phase/relevance, spring tide). It reads the same `conditions` table in
Supabase that your Cloudflare Worker already keeps fresh, so "today's top
beach" here always matches what the app itself would show. **If you change
the scoring logic or beach list in the app, mirror the change in
`beach_data.py`** — it's a deliberate duplicate (Swift vs Python), not a
shared import.

## Files

- `beach_data.py` — beach list + scoring (ported from the app)
- `facts.py` — evening fact bank (beach facts + app facts, rotates by date)
- `copy_gen.py` — punchy caption templates (no LLM — free, deterministic)
- `palette.py` — the brand colours (see below)
- `branding.py` — the logo/icon marks (Table Mountain + sun + waves), drawn as shapes, not imported art
- `image_gen.py` — renders the 1080×1080 post image with Pillow
- `supabase_client.py` — reads latest conditions (read-only, same anon key already in your shipped app)
- `instagram_api.py` — Graph API publish (2-step: create container → publish)
- `main.py` — orchestrator (`render` then `publish`, see workflow)
- `.github/workflows/social-posts.yml` — the schedule + pipeline
- `assets/logos/` — standalone exported logo/icon PNGs (app icon, transparent icon, wordmark lockup) for use outside the posts
- `SETUP.md` — **read this first** — the one-time Meta/Instagram setup only you can do
- `STYLEGUIDE.md` — the brand guide: colour/type/logo rules and the voice/copy rules, both enforced by the code above
- `STRATEGY.md` — the growth strategy: sourced research on what actually drives Instagram discovery for a small/new account, and a daily/weekly/monthly action plan
- `PRIVACY.md` / `privacy-policy.html` — the privacy policy for the Meta Developer App ("Beach, Please App") and the iOS app, grounded in what the app's own code actually does

## The palette — "sophisticated fun in the sun"

Bright tropical pink + teal-leaning lagoon blue + a light sunny yellow,
grounded by a deep ink and warm cream so it reads resort-chic rather than
kids'-party bright:

| | Hex | Use |
|---|---|---|
| Teal Deep | `#0B7C82` | primary brand colour, backgrounds |
| Teal Bright | `#2FE0D6` | gradients |
| Pink | `#FF4FA0` | the "fun" accent — CTAs, headline banners |
| Yellow | `#FFDE7A` | secondary accent, tags |
| Cream | `#FFF8EC` | light backgrounds/cards |
| Ink | `#0B2E33` | body text |

The "Beach, Please!" wordmark is set in Sacramento (script) rather than
Poppins, everywhere it appears as a footer/signature.

Swap these in `palette.py` if you want to art-direct it differently — every
other file reads from there, nothing is hard-coded elsewhere.

## The mark

An original, simplified Table Mountain silhouette (Lion's Head → the flat
plateau → Devil's Peak) + a sun + wave lines, drawn as shapes in
`branding.py` rather than imported artwork — so it scales cleanly and
recolours with the palette. Every post carries it in the footer (icon +
the Sacramento script wordmark); standalone exports for other uses (app
icon, profile picture, a website header) are in `assets/logos/`.

Full usage rules (minimum clear space, do/don't recolour, backgrounds) are
in `STYLEGUIDE.md`, along with the voice/copy rules for captions.

## Local testing

```
pip install -r requirements.txt
export GITHUB_REPOSITORY="YOUR_USERNAME/beach-please-social"
python3 main.py render morning
python3 main.py publish morning   # prints a dry run until IG secrets are set
```

## What's still manual

Meta requires your own login for the Instagram Business/Facebook Page/
Developer app setup — see `SETUP.md`. Everything else here is done and
tested (in dry-run).
