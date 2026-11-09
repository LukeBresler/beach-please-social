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
from branding import draw_mountain, draw_sun, draw_waves, draw_wordmark_lockup

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


# ---------------------------------------------------------------------------
# Seven designs, rotated. Every post takes the next theme in the cycle, so two
# consecutive posts never share a design and the whole cycle repeats each week
# (3 posts a day x 7 days = 21 posts = 3 full turns of 7 themes).
# Consecutive themes differ in palette, background and layout (A/B/C).
# ---------------------------------------------------------------------------
LAYOUT_A, LAYOUT_B, LAYOUT_C = "A", "B", "C"

THEMES = [
    dict(name="lagoon", layout=LAYOUT_A,
         spot_bg=("grad", TEAL_DEEP, TEAL_BRIGHT), fact_bg=("grad", PINK, TEAL_DEEP),
         ink=WHITE, sub=CREAM, tag=YELLOW, tag_text=INK, pill=PINK, pill_text=WHITE,
         card=CREAM, ground="#095F64", fact_ground="#085A5F", sun=YELLOW,
         opener=YELLOW, foot=TEAL_DEEP, foot_sun=PINK, fact_foot=YELLOW, fact_foot_sun=CREAM),
    dict(name="sunset", layout=LAYOUT_B,
         spot_bg=("grad", "#7A1F5C", PINK), fact_bg=("grad", "#6B1A55", PINK),
         ink=WHITE, sub=CREAM, tag=YELLOW, tag_text=INK, pill=YELLOW, pill_text=INK,
         card=CREAM, ground="#4A1038", fact_ground="#4A1038", sun=YELLOW,
         opener=YELLOW, foot=CREAM, foot_sun=YELLOW, fact_foot=CREAM, fact_foot_sun=YELLOW),
    dict(name="sand", layout=LAYOUT_C,
         spot_bg=("solid", CREAM), fact_bg=("solid", TEAL_DEEP),
         ink=INK, sub=TEAL_DEEP, tag=TEAL_DEEP, tag_text=WHITE, pill=PINK, pill_text=WHITE,
         card=CREAM, ground=TEAL_DEEP, fact_ground="#085A5F", sun=PINK,
         opener=YELLOW, foot=CREAM, foot_sun=YELLOW, fact_foot=CREAM, fact_foot_sun=YELLOW),
    dict(name="midnight", layout=LAYOUT_B,
         spot_bg=("grad", INK, TEAL_DEEP), fact_bg=("grad", INK, "#0F5A60"),
         ink=WHITE, sub=TEAL_BRIGHT, tag=YELLOW, tag_text=INK, pill=PINK, pill_text=WHITE,
         card=CREAM, ground="#061C20", fact_ground="#061C20", sun=YELLOW,
         opener=TEAL_BRIGHT, foot=CREAM, foot_sun=YELLOW, fact_foot=CREAM, fact_foot_sun=YELLOW),
    dict(name="sunrise", layout=LAYOUT_A,
         spot_bg=("grad", YELLOW, "#FF8A5B"), fact_bg=("grad", "#D9480F", PINK),
         ink=INK, sub=INK, tag=TEAL_DEEP, tag_text=WHITE, pill=TEAL_DEEP, pill_text=WHITE,
         card=CREAM, ground="#C4472C", fact_ground="#8A1F3C", sun=YELLOW,
         opener=YELLOW, foot=TEAL_DEEP, foot_sun=PINK, fact_foot=YELLOW, fact_foot_sun=CREAM),
    dict(name="seafoam", layout=LAYOUT_C,
         spot_bg=("grad", TEAL_BRIGHT, "#8FF0E6"), fact_bg=("grad", "#16A6AA", "#0B4F55"),
         ink=INK, sub=INK, tag=INK, tag_text=WHITE, pill=PINK, pill_text=WHITE,
         card=CREAM, ground="#0B6168", fact_ground="#083F44", sun=YELLOW,
         opener=YELLOW, foot=CREAM, foot_sun=YELLOW, fact_foot=CREAM, fact_foot_sun=YELLOW),
    dict(name="punch", layout=LAYOUT_B,
         spot_bg=("solid", "#E0307F"), fact_bg=("solid", "#E0307F"),
         ink=WHITE, sub=CREAM, tag=YELLOW, tag_text=INK, pill=INK, pill_text=WHITE,
         card=CREAM, ground="#A81C5E", fact_ground="#A81C5E", sun=YELLOW,
         opener=YELLOW, foot=CREAM, foot_sun=YELLOW, fact_foot=CREAM, fact_foot_sun=YELLOW),
]

SLOT_INDEX = {"morning": 0, "noon": 1, "evening": 2}


def pick_theme(date, slot: str) -> dict:
    """Theme for a post: advances by one per post, so neighbours always differ."""
    return THEMES[(3 * date.toordinal() + SLOT_INDEX.get(slot, 0)) % len(THEMES)]


def _background(bg):
    if bg[0] == "solid":
        return Image.new("RGB", (W, H), _hex_to_rgb(bg[1]))
    return _vertical_gradient((W, H), bg[1], bg[2])


def _tag(draw, text, x, y, t):
    f = _font(F_BOLD, 30)
    w = draw.textlength(text, font=f) + 48
    _rounded_rect(draw, (x, y, x + w, y + 62), 31, _hex_to_rgb(t["tag"]))
    draw.text((x + 24, y + 12), text, font=f, fill=_hex_to_rgb(t["tag_text"]))
    return w


def _badge(draw, cx, cy, r, score, num_size, lab_size):
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_hex_to_rgb(score_color(score)))
    nf = _font(F_BOLD, num_size)
    txt = f"{score}%"
    draw.text((cx - draw.textlength(txt, font=nf) / 2, cy - num_size * 0.62), txt, font=nf, fill=_hex_to_rgb(INK))
    lf = _font(F_MEDIUM, lab_size)
    draw.text((cx - draw.textlength("match", font=lf) / 2, cy + num_size * 0.4), "match", font=lf, fill=_hex_to_rgb(INK))


def _centered_lines(draw, lines, font, y, fill, line_h):
    for ln in lines:
        draw.text(((W - draw.textlength(ln, font=font)) / 2, y), ln, font=font, fill=_hex_to_rgb(fill))
        y += line_h
    return y


def render_spot_card(beach_name: str, kind_label: str, score: int, temp,
                      protection_text: str, headline: str, out_path: str,
                      badges: list = None, theme: dict = None):
    """The morning/noon 'top spot' card, in the given theme (default: lagoon).
    Layout A: name on the hero, wavy cream card below. B: centred, big score,
    mountain band at the base. C: sun setting behind the mountain, name on the sea."""
    t = theme or THEMES[0]
    img = _background(t["spot_bg"])
    draw = ImageDraw.Draw(img)
    margin = 88
    sub_text = f"{temp:.0f}°C · {protection_text}" if temp is not None else protection_text
    name_font = _font(F_BOLD, 88)
    sub_font = _font(F_MEDIUM, 40)
    tag_text = kind_label.upper()

    if t["layout"] == LAYOUT_A:
        wave_top = H - 380
        draw_mountain(draw, 0, wave_top + 24, W, 210, fill=t["ground"])
        _tag(draw, tag_text, margin, margin, t)
        _badge(draw, W - margin - 90, margin + 90, 90, score, 54, 22)
        name_y = 380
        for line in _wrap_text(draw, beach_name, name_font, W - margin * 2)[:2]:
            draw.text((margin, name_y), line, font=name_font, fill=_hex_to_rgb(t["ink"]))
            name_y += 100
        for line in _wrap_text(draw, sub_text, sub_font, W - margin * 2):
            draw.text((margin, name_y + 16), line, font=sub_font, fill=_hex_to_rgb(t["sub"]))
            name_y += 54
        _wavy_card(draw, wave_top, amplitude=16, fill=t["card"])
        draw.rounded_rectangle((margin - 24, wave_top - 10, W - margin + 24, wave_top + 70), radius=24, fill=_hex_to_rgb(t["pill"]))
        hf = _font(F_BOLD, 34)
        hw = draw.textlength(headline.upper(), font=hf)
        draw.text(((W - hw) / 2, wave_top + 20), headline.upper(), font=hf, fill=_hex_to_rgb(t["pill_text"]))
        bf = _font(F_REGULAR, 32)
        by = wave_top + 100
        for line in _wrap_text(draw, "Live-scored from today's wind, tide and water temperature.", bf, W - margin * 2)[:2]:
            draw.text((margin, by), line, font=bf, fill=_hex_to_rgb(INK))
            by += 42
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 130, scale=1.0, text_color=t["foot"], sun_color=t["foot_sun"])

    elif t["layout"] == LAYOUT_B:
        base = H - 170
        draw_sun(draw, W - 190, 210, 70, fill=t["sun"], rays=True)
        draw_mountain(draw, 0, base, W, 150, fill=t["ground"])
        draw.rectangle((0, base, W, H), fill=_hex_to_rgb(t["ground"]))
        draw_waves(draw, 0, base + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)
        tf = _font(F_BOLD, 30)
        tw = draw.textlength(tag_text, font=tf) + 48
        _tag(draw, tag_text, (W - tw) / 2, 120, t)
        _badge(draw, W / 2, 390, 140, score, 84, 30)
        y = 570
        y = _centered_lines(draw, _wrap_text(draw, beach_name, name_font, W - margin * 2)[:2], name_font, y, t["ink"], 100)
        y = _centered_lines(draw, _wrap_text(draw, sub_text, sub_font, W - margin * 2)[:2], sub_font, y + 8, t["sub"], 54)
        hf = _font(F_BOLD, 32)
        hw = draw.textlength(headline.upper(), font=hf) + 64
        py = max(y + 24, 900)
        draw.rounded_rectangle(((W - hw) / 2, py, (W + hw) / 2, py + 72), radius=36, fill=_hex_to_rgb(t["pill"]))
        draw.text(((W - hw) / 2 + 32, py + 17), headline.upper(), font=hf, fill=_hex_to_rgb(t["pill_text"]))
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 125, scale=0.9, text_color=t["foot"], mountain_color=t["foot"], sun_color=t["foot_sun"])

    else:  # LAYOUT_C
        horizon = 700
        draw_sun(draw, W * 0.66, horizon - 120, 190, fill=t["sun"], rays=False)
        draw_mountain(draw, 0, horizon, W, 190, fill=t["ground"])
        draw.rectangle((0, horizon, W, H), fill=_hex_to_rgb(t["ground"]))
        draw_waves(draw, 0, horizon + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)
        _tag(draw, tag_text, margin, margin, t)
        _badge(draw, W - margin - 90, margin + 90, 90, score, 54, 22)
        hf = _font(F_BOLD, 30)
        draw.text((margin, 750), headline.upper(), font=hf, fill=_hex_to_rgb(YELLOW))
        y = 810
        for line in _wrap_text(draw, beach_name, name_font, W - margin * 2)[:2]:
            draw.text((margin, y), line, font=name_font, fill=_hex_to_rgb(WHITE))
            y += 100
        for line in _wrap_text(draw, sub_text, sub_font, W - margin * 2)[:2]:
            draw.text((margin, y + 8), line, font=sub_font, fill=_hex_to_rgb(CREAM))
            y += 54
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 125, scale=0.9, text_color=t["foot"], mountain_color=t["foot"], sun_color=t["foot_sun"])

    img.save(out_path, "JPEG", quality=92)
    return out_path


def render_fact_card(opener: str, fact_text: str, out_path: str, theme: dict = None):
    """The evening fact card in the given theme (default: lagoon).
    A: centred over a mountain band. B: left-aligned with a sun. C: big sun behind the mountain."""
    t = theme or THEMES[0]
    img = _background(t["fact_bg"])
    draw = ImageDraw.Draw(img)
    margin = 96
    ground = t["fact_ground"]
    opener_font = _font(F_BOLD, 44)

    if t["layout"] == LAYOUT_A:
        base = H - 150
        draw_mountain(draw, 0, base, W, 190, fill=ground)
        draw.rectangle((0, base, W, H), fill=_hex_to_rgb(ground))
        draw_waves(draw, 0, base + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)
        ow = draw.textlength(opener.upper(), font=opener_font)
        draw.text(((W - ow) / 2, 270), opener.upper(), font=opener_font, fill=_hex_to_rgb(t["opener"]))
        ff = _font(F_MEDIUM, 50)
        y = 390
        for line in _wrap_text(draw, fact_text, ff, W - margin * 2):
            draw.text(((W - draw.textlength(line, font=ff)) / 2, y), line, font=ff, fill=_hex_to_rgb(WHITE))
            y += 64
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 120, scale=0.9, text_color=t["fact_foot"], mountain_color=t["fact_foot"], sun_color=t["fact_foot_sun"])

    elif t["layout"] == LAYOUT_B:
        base = H - 150
        draw_sun(draw, W - 170, 170, 80, fill=t["sun"], rays=True)
        draw_mountain(draw, 0, base, W, 150, fill=ground)
        draw.rectangle((0, base, W, H), fill=_hex_to_rgb(ground))
        draw_waves(draw, 0, base + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)
        draw.rounded_rectangle((margin, 250, margin + 120, 262), radius=6, fill=_hex_to_rgb(t["opener"]))
        draw.text((margin, 290), opener.upper(), font=opener_font, fill=_hex_to_rgb(t["opener"]))
        ff = _font(F_MEDIUM, 54)
        y = 390
        for line in _wrap_text(draw, fact_text, ff, W - margin * 2):
            draw.text((margin, y), line, font=ff, fill=_hex_to_rgb(WHITE))
            y += 70
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 120, scale=0.9, text_color=t["fact_foot"], mountain_color=t["fact_foot"], sun_color=t["fact_foot_sun"])

    else:  # LAYOUT_C
        horizon = H - 300
        draw_sun(draw, W / 2, horizon - 110, 230, fill=t["sun"], rays=False)
        draw_mountain(draw, 0, horizon, W, 240, fill=ground)
        draw.rectangle((0, horizon, W, H), fill=_hex_to_rgb(ground))
        draw_waves(draw, 0, horizon + 4, W, amplitude=6, fill=WHITE, lines=1, spacing=16)
        ow = draw.textlength(opener.upper(), font=opener_font)
        draw.text(((W - ow) / 2, 170), opener.upper(), font=opener_font, fill=_hex_to_rgb(t["opener"]))
        ff = _font(F_MEDIUM, 50)
        y = 270
        for line in _wrap_text(draw, fact_text, ff, W - margin * 2):
            draw.text(((W - draw.textlength(line, font=ff)) / 2, y), line, font=ff, fill=_hex_to_rgb(WHITE))
            y += 64
        draw_wordmark_lockup(draw, cx=W / 2, y=H - 215, scale=0.9, text_color=t["fact_foot"], mountain_color=t["fact_foot"], sun_color=t["fact_foot_sun"])

    img.save(out_path, "JPEG", quality=92)
    return out_path
