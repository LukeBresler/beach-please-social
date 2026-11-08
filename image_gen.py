"""
Renders 1080x1080 Instagram-square post images with Pillow -- no headless
browser, no external rendering service, just fonts + shapes. Keeps the
whole pipeline dependency-light and free to run on GitHub Actions' free
Linux runners.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

from palette import TEAL_DEEP, TEAL_BRIGHT, PINK, YELLOW, CREAM, INK, WHITE, score_color
from branding import draw_mountain, draw_waves, draw_wordmark_lockup

W = 1080
H = 1350   # 4:5 portrait. The 3:4 profile grid then crops only ~34 px per side (a square lost 135 px)
SIZE = W

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
F_BOLD = f"{FONT_DIR}/Poppins-Bold.ttf"
F_MEDIUM = f"{FONT_DIR}/Poppins-Medium.ttf"
F_REGULAR = f"{FONT_DIR}/Poppins-Regular.ttf"
F_LIGHT = f"{FONT_DIR}/Poppins-Light.ttf"


def _font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _hex_to_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _darken(h: str, amount: float = 0.18) -> tuple:
    r, g, b = _hex_to_rgb(h)
    return (int(r * (1 - amount)), int(g * (1 - amount)), int(b * (1 - amount)))


def _vertical_gradient(size, top_hex, bottom_hex):
    top = _hex_to_rgb(top_hex)
    bottom = _hex_to_rgb(bottom_hex)
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    h = size[1]
    for y in range(h):
        t = y / h
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        draw.line([(0, y), (size[0], y)], fill=(r, g, b))
    return img


def _rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def _wavy_card(draw, top_y, amplitude, fill, width=W, height=H):
    """Fills from a gentle sine-wave 'shoreline' down to the bottom of the
    canvas -- the cream card meeting the water, instead of a hard cut."""
    steps = 48
    points = [(0, height)]
    for s in range(steps + 1):
        t = s / steps
        x = t * width
        y = top_y + math.sin(t * math.pi * 2.2) * amplitude
        points.append((x, y))
    points.append((width, height))
    draw.polygon(points, fill=_hex_to_rgb(fill) if isinstance(fill, str) else fill)


def _wrap_text(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def render_spot_card(beach_name: str, kind_label: str, score: int, temp,
                      protection_text: str, headline: str, out_path: str,
                      badges: list = None):
    """
    The morning/noon "top spot" card: tropical teal gradient hero with a
    Table Mountain silhouette on the horizon, a wavy shoreline into the
    cream card below, big score badge, beach name, and a mountain+sun+
    script wordmark footer.
    """
    img = _vertical_gradient((W, H), TEAL_DEEP, TEAL_BRIGHT)
    draw = ImageDraw.Draw(img)

    margin = 88
    wave_top = H - 380

    # Table Mountain on the horizon, sitting just above the shoreline
    mountain_h = 210
    draw_mountain(draw, 0, wave_top + 24, W, mountain_h, fill=_darken(TEAL_DEEP, 0.22))

    # Kind tag (BEACH / TIDAL POOL) -- sunny yellow, the "light yellow notes"
    tag_font = _font(F_BOLD, 30)
    tag_text = kind_label.upper()
    tag_w = draw.textlength(tag_text, font=tag_font) + 48
    _rounded_rect(draw, (margin, margin, margin + tag_w, margin + 62), 31, _hex_to_rgb(YELLOW))
    draw.text((margin + 24, margin + 12), tag_text, font=tag_font, fill=_hex_to_rgb(INK))

    # Score badge, top-right -- circular, colour-coded status (green/yellow/pink)
    badge_r = 90
    badge_cx, badge_cy = W - margin - badge_r, margin + badge_r
    draw.ellipse(
        (badge_cx - badge_r, badge_cy - badge_r, badge_cx + badge_r, badge_cy + badge_r),
        fill=_hex_to_rgb(score_color(score)),
    )
    score_font = _font(F_BOLD, 54)
    score_text = f"{score}%"
    tw = draw.textlength(score_text, font=score_font)
    draw.text((badge_cx - tw / 2, badge_cy - 34), score_text, font=score_font, fill=_hex_to_rgb(INK))
    small_font = _font(F_MEDIUM, 22)
    label_text = "match"
    tw2 = draw.textlength(label_text, font=small_font)
    draw.text((badge_cx - tw2 / 2, badge_cy + 22), label_text, font=small_font, fill=_hex_to_rgb(INK))

    # Beach name -- big headline, wrapped
    name_font = _font(F_BOLD, 88)
    name_y = 380
    wrapped_name = _wrap_text(draw, beach_name, name_font, W - margin * 2)
    for line in wrapped_name[:2]:
        draw.text((margin, name_y), line, font=name_font, fill=_hex_to_rgb(WHITE))
        name_y += 100

    # Punchy sub-line
    sub_font = _font(F_MEDIUM, 40)
    sub_text = f"{temp:.0f}°C · {protection_text}" if temp is not None else protection_text
    for line in _wrap_text(draw, sub_text, sub_font, W - margin * 2):
        draw.text((margin, name_y + 16), line, font=sub_font, fill=_hex_to_rgb(CREAM))
        name_y += 54

    # Wavy shoreline into the cream card
    _wavy_card(draw, wave_top, amplitude=16, fill=CREAM)

    card_top = wave_top
    draw.rounded_rectangle((margin - 24, card_top - 10, W - margin + 24, card_top + 70), radius=24, fill=_hex_to_rgb(PINK))
    headline_font = _font(F_BOLD, 34)
    hw = draw.textlength(headline.upper(), font=headline_font)
    draw.text(((W - hw) / 2, card_top + 20), headline.upper(), font=headline_font, fill=_hex_to_rgb(WHITE))

    body_font = _font(F_REGULAR, 32)
    body_y = card_top + 100
    for line in _wrap_text(draw, "Live-scored from today's wind, tide and water temperature.", body_font, W - margin * 2)[:2]:
        draw.text((margin, body_y), line, font=body_font, fill=_hex_to_rgb(INK))
        body_y += 42

    # Icon + script wordmark footer
    draw_wordmark_lockup(draw, cx=W / 2, y=H - 130, scale=1.0, text_color=TEAL_DEEP, sun_color=PINK)

    img.save(out_path, "JPEG", quality=92)
    return out_path


def render_fact_card(opener: str, fact_text: str, out_path: str):
    """The evening fact card: tropical pink-to-teal dusk gradient, Table
    Mountain silhouette + waves at the base, centred text."""
    img = _vertical_gradient((W, H), PINK, TEAL_DEEP)
    draw = ImageDraw.Draw(img)
    margin = 96

    # Mountain + waves grounding the bottom of the card
    mountain_h = 190
    mountain_base = H - 150
    ground = _darken(TEAL_DEEP, 0.28)
    draw_mountain(draw, 0, mountain_base, W, mountain_h, fill=ground)
    draw.rectangle((0, mountain_base, W, H), fill=ground)   # solid band so the wordmark never sits on wave lines
    draw_waves(draw, 0, mountain_base + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)

    opener_font = _font(F_BOLD, 44)
    ow = draw.textlength(opener.upper(), font=opener_font)
    draw.text(((W - ow) / 2, 270), opener.upper(), font=opener_font, fill=_hex_to_rgb(YELLOW))

    fact_font = _font(F_MEDIUM, 50)
    lines = _wrap_text(draw, fact_text, fact_font, W - margin * 2)
    total_h = len(lines) * 64
    y = 390
    for line in lines:
        lw = draw.textlength(line, font=fact_font)
        draw.text(((W - lw) / 2, y), line, font=fact_font, fill=_hex_to_rgb(WHITE))
        y += 64

    # Icon + script wordmark footer, sitting over the mountain
    draw_wordmark_lockup(draw, cx=W / 2, y=H - 120, scale=0.9, text_color=YELLOW, mountain_color=YELLOW, sun_color=CREAM)

    img.save(out_path, "JPEG", quality=92)
    return out_path
