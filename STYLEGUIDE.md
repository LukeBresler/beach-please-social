# Beach, Please! — Brand Style Guide

One page you (or anyone else who ever touches this brand — a future
contributor, a designer, an Android build) can read start to finish and
know how to write and design for Beach, Please! without asking.

## Brand essence

**Sophisticated fun in the sun.** Bright and warm, never childish; playful
copy, never sloppy design. Think a well-designed boutique resort's
Instagram, not a kids' beach-ball ad. The tension to hold: *fun* comes from
colour and voice; *sophistication* comes from restraint — generous white
space, one accent colour at a time, short copy.

If a design or a line of copy feels like it's trying too hard, it's
probably not sophisticated enough yet, not "not fun enough."

---

## Part 1 — Design

### Colour

| | Hex | Role |
|---|---|---|
| Teal Deep | `#0B7C82` | Primary brand colour. Backgrounds, wordmark, mountain fills. |
| Teal Bright | `#2FE0D6` | Gradient partner to Teal Deep. Never used alone. |
| Pink | `#FF4FA0` | The one "fun" accent. CTAs, headline banners, low-score badge. Use once per composition — two pink elements fighting for attention breaks "sophisticated." |
| Yellow | `#FFDE7A` | Secondary accent. Tags, sun icon, mid-score badge, small warm touches. Never a large fill — it's a highlight colour, not a background colour. |
| Cream | `#FFF8EC` | Light backgrounds/cards. Warmer than white on purpose — avoids the "clinical app" look. |
| Ink | `#0B2E33` | All body text. Never pure black — it's a deep teal-black, which is why text still feels like it belongs to this palette. |

**Rules:**
- Every composition gets a teal gradient *or* a cream/light base — not both fighting on equal footing. One is the ground, the other is the figure.
- Pink and yellow are accents, not co-equal brand colours with teal. If you're reaching for a third saturated colour in one spot, stop.
- Status colours (score badges: green/yellow/pink) are a separate system from brand colours, on purpose — a score badge should never be mistaken for a piece of the logo.
- Never place Ink text on Teal Bright or Yellow without checking contrast — both are light enough that Ink needs real size/weight to stay legible.

### Typography

- **Poppins** (Bold / Medium / Regular / Light) — everything except the wordmark. Bold for headlines and numbers, Medium for sub-lines and UI labels, Regular for body copy.
- **Sacramento** (script) — the wordmark *only*. Never set body copy, captions, or anything functional in script — it's a signature, not a reading font. Never go below ~60px rendered size; it degrades fast.
- Don't introduce a third typeface. If Poppins/Sacramento can't do it, that's a sign to redesign the layout, not add a font.

### The mark

Two forms, both built from the same three shapes (Table Mountain silhouette
+ sun + wave lines) — an original simplified line drawing of the real
mountain profile (Lion's Head → the long flat plateau → Devil's Peak), not
a stock icon:

- **Icon mark** (`icon_transparent.png`, `app_icon.png`) — mountain + sun,
  no text. For anything small or square: app icon, favicon, social profile
  picture.
- **Wordmark lockup** (`logo_lockup_*.png`) — icon + "Beach, Please!" in
  Sacramento, side by side. For anything with room to breathe: post
  footers, a website header, email signature.

**Rules:**
- Never stretch, skew, or recolour the mountain shape outside the brand palette (it can go teal-on-cream, cream-on-teal, or yellow-on-teal — see the fact-card footer — but not, say, orange or grey).
- Minimum clear space around the lockup: roughly one icon-height on all sides. Don't crowd it against text or a frame edge.
- On a busy or photographic background, the mark needs a solid or near-solid colour block behind it (as in the post footers) — never drop it directly onto a photo.
- Don't use the icon mark and a separate, different "Beach, Please!" text treatment in the same composition — if text is present, use the lockup, not the icon alone plus some other font.

### Layout pattern (social posts)

Every post follows the same bones, which is what makes the feed read as
one brand even though the content changes 3x/day:

1. **Gradient hero** (top) — teal gradient, or pink-to-teal for evening
   posts. Mountain silhouette on the horizon. This is where the "big
   number" or headline photo-substitute lives.
2. **Wavy shoreline transition** — never a hard horizontal cut between
   hero and card. The sine-wave edge is doing real brand work: it's the
   one shape that says "coast" without needing a photo.
3. **Cream card** (bottom) — body copy, always Ink-on-Cream for maximum
   legibility, closed out with the wordmark lockup.
4. One pink banner per card, maximum, for the single most important line
   (the headline). If everything is banner-highlighted, nothing is.

### Imagery (when real photos enter the mix)

Not used yet (current posts are graphic-only), but if/when real beach
photography gets added:
- Bright, high-key, real Cape Town locations only — no generic stock
  "tropical beach" photos that could be anywhere.
  photos of Cape Town specifically, not passable resemblances.
- Warm colour grading that leans toward the palette (don't fight the teal/
  pink/yellow with a cold blue-grey photo grade).
- A photo always needs a scrim (gradient overlay) before text sits on it —
  never raw white text directly on a busy photo.

---

## Part 2 — Content & voice

### Voice in one line

**A sharp local friend who actually checked the wind, not a tourism
board.** Specific, current, a little cheeky. Never generic travel-blog
language ("breathtaking," "hidden gem," "must-visit").

### Rules

- **Lead with the verdict, not the setup.** "Llandudno's the call" beats "Looking for a great beach today? Check out Llandudno!"
- **One real, specific detail beats three adjectives.** "3,000 penguins, 540-million-year-old granite" beats "stunning natural beauty."
- **Short sentences. Fragments are fine.** "Grab your towel." "No excuses left." This is Instagram caption rhythm, not app-copy rhythm.
- **Never oversell a bad day.** If the score is 60%, the copy says so plainly ("exposed today — go in with eyes open"). Confidently telling people the truth is part of what makes the brand feel trustworthy, not the same as being negative.
- **No stacked emoji, no exclamation-mark chains.** One emoji maximum per caption if any; the palette and layout already carry the "fun," the copy doesn't need to shout to match.
- **Hashtags are a footer, not a sentence.** Always the same small, relevant set (`#BeachPlease #CapeTown #CapeTownBeaches...`) — never mid-sentence, never more than 5.
- **Facts get told straight, not hyped.** "Built in 1907" doesn't need "Can you believe it?!" bolted on.

### What "sophisticated fun" sounds like vs. doesn't

| Sophisticated fun ✅ | Trying too hard ❌ |
|---|---|
| "Today's call: Llandudno. 94% match." | "OMG you guys, Llandudno is AMAZING today!! 🏖️🌊☀️" |
| "Exposed today — go in with eyes open." | "Not the best day, sorry! 😅 Maybe tomorrow!" |
| "Boulders Beach: ~3,000 penguins, granite over 540 million years old." | "Fun fact: penguins are SO cute and this beach is EPIC!" |

### Where this lives in code

Nothing above is arbitrary — it maps directly onto the pipeline so voice
and design stay enforced automatically, not just documented:
- `copy_gen.py` — the templates that encode the voice rules above
- `palette.py` — the colour table above, literally
- `branding.py` / `image_gen.py` — the mark and layout pattern above

If you're extending this (new post type, new platform, the future Android
app), start by reading those files with this guide open — the code *is*
the enforcement mechanism for the brand, not a separate thing from it.
