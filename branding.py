"""
Beach, Please! logo marks -- drawn as shapes (not imported art), so they
scale cleanly to any size and stay pixel-consistent everywhere they're
used: post footers, a standalone icon/profile picture, and an app-icon
candidate. Everything reads from palette.py, so a palette change here
updates every mark at once.

The mountain silhouette is a simplified, original line drawing of Table
Mountain's real profile (Lion's Head -> saddle -> the long flat plateau ->
Devil's Peak) -- a real place's outline, not anyone's copyrighted artwork.
"""

import os
from PIL import Image, ImageDraw, ImageFont

from palette import TEAL_DEEP, TEAL_BRIGHT, PINK, YELLOW, CREAM, INK, WHITE

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts")
F_SCRIPT = f"{FONT_DIR}/Sacramento-Regular.ttf"
F_BOLD = f"{FONT_DIR}/Poppins-Bold.ttf"


def _hex_to_rgb(h: str, alpha: int = None) -> tuple:
    h = h.lstrip("#")
    rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    return rgb if alpha is None else rgb + (alpha,)


def _mountain_points(x0: float, y0: float, w: float, h: float) -> list:
    """
    Table Mountain's profile, traced from a reference outline and
    normalised to a (w x h) box anchored at bottom-left (x0, y0).
    Left -> right: the low western flank climbing to Lion's Head, a notch
    at Kloof Nek, the long flat plateau (rising very slightly to the
    east), a step down at the plateau's end, the sloping eastern
    shoulder into a valley, then the bump of Devil's Peak and the
    descent to the right edge.
    """
    pts = [
        (0.000, 1.00),   # base, far left
        (0.000, 0.93),   # low western flank
        (0.055, 0.70),
        (0.086, 0.55),
        (0.117, 0.46),
        (0.140, 0.29),   # climbing to Lion's Head
        (0.152, 0.15),   # Lion's Head peak
        (0.176, 0.14),
        (0.203, 0.21),
        (0.233, 0.29),   # Kloof Nek notch
        (0.246, 0.16),
        (0.258, 0.115),  # plateau front edge
        (0.625, 0.010),  # the long flat top, rising slightly to the east
        (0.640, 0.036),
        (0.652, 0.180),  # step down at the plateau's end
        (0.680, 0.210),
        (0.695, 0.390),
        (0.715, 0.550),
        (0.738, 0.660),  # valley
        (0.762, 0.550),
        (0.805, 0.520),
        (0.828, 0.300),
        (0.842, 0.280),  # Devil's Peak
        (0.863, 0.340),
        (0.879, 0.460),
        (0.938, 0.650),
        (1.000, 0.810),  # eastern flank, far right
        (1.000, 1.00),   # base, far right
    ]
    return [(x0 + px * w, y0 - h + py * h) for px, py in pts]


def _mountain_points_simple(x0: float, y0: float, w: float, h: float) -> list:
    """
    A bolder, simpler Table Mountain for small sizes (footer lockup, app
    icon). Same landmarks as the full outline (Lion's Head, the notch, the
    flat plateau, the step, Devil's Peak) but with fewer, chunkier
    features and a friendlier aspect ratio, so it doesn't turn to mush
    when it is only ~100 px wide.
    """
    pts = [
        (0.00, 1.00),
        (0.00, 0.78),
        (0.09, 0.52),
        (0.17, 0.18),   # Lion's Head
        (0.24, 0.30),
        (0.31, 0.46),   # notch
        (0.36, 0.12),   # plateau front
        (0.72, 0.02),   # plateau top
        (0.77, 0.22),   # step down
        (0.83, 0.62),   # valley
        (0.90, 0.30),   # Devil's Peak
        (1.00, 0.72),
        (1.00, 1.00),
    ]
    return [(x0 + px * w, y0 - h + py * h) for px, py in pts]


def _chaikin(pts: list, iterations: int = 2) -> list:
    """Corner-cutting smoothing: each pass replaces every corner with two
    points a quarter of the way along its neighbours, so straight runs stay
    straight and angular joins turn into soft curves. First and last
    points are pinned."""
    for _ in range(iterations):
        out = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            out.append((0.75 * ax + 0.25 * bx, 0.75 * ay + 0.25 * by))
            out.append((0.25 * ax + 0.75 * bx, 0.25 * ay + 0.75 * by))
        out.append(pts[-1])
        pts = out
    return pts


def _composite(dest: Image.Image, mask: Image.Image, rgb: tuple):
    """Paint a solid colour onto dest through an antialiased mask."""
    if dest.mode == "RGBA":
        over = Image.new("RGBA", dest.size, tuple(rgb) + (0,))
        over.putalpha(mask)
        dest.alpha_composite(over)
    else:
        dest.paste(Image.new("RGB", dest.size, tuple(rgb)), (0, 0), mask)


def draw_mountain(draw: ImageDraw.ImageDraw, x0, y0, w, h, fill, simple=False):
    """Smoothed and antialiased: the outline's corners are rounded off,
    then it is drawn 4x larger on a transparent layer, scaled down and
    composited, so edges stay smooth at every size."""
    pts = (_mountain_points_simple if simple else _mountain_points)(x0, y0, w, h)
    # pts[0] and pts[-1] are the two base corners; smooth only the skyline between them
    pts = [pts[0]] + _chaikin(pts[1:-1], 2) + [pts[-1]]
    rgb = _hex_to_rgb(fill) if isinstance(fill, str) else tuple(fill)[:3]
    dest = draw._image
    k = 4
    layer = Image.new("L", (dest.width * k, dest.height * k), 0)
    ImageDraw.Draw(layer).polygon([(x * k, y * k) for x, y in pts], fill=255)
    _composite(dest, layer.resize(dest.size, Image.LANCZOS), rgb)


def draw_sun(draw: ImageDraw.ImageDraw, cx, cy, r, fill, rays=True, ray_fill=None, upper_only=False):
    if rays:
        ray_fill = ray_fill or fill
        import math
        n = 12
        for i in range(n):
            angle = (2 * math.pi / n) * i
            if upper_only and math.sin(angle) > 0.2:   # skip rays that point down (y grows downward)
                continue
            x1 = cx + math.cos(angle) * r * 1.35
            y1 = cy + math.sin(angle) * r * 1.35
            x2 = cx + math.cos(angle) * r * 1.7
            y2 = cy + math.sin(angle) * r * 1.7
            draw.line([(x1, y1), (x2, y2)], fill=_hex_to_rgb(ray_fill) if isinstance(ray_fill, str) else ray_fill, width=max(2, int(r * 0.09)))
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=_hex_to_rgb(fill) if isinstance(fill, str) else fill)


def draw_waves(draw: ImageDraw.ImageDraw, x0, y, w, amplitude, fill, lines=3, spacing=None):
    """Smooth sine waves, drawn at 4x and scaled down so the lines have no
    kinks or stair-steps."""
    import math
    spacing = spacing or amplitude * 2.2
    rgb = _hex_to_rgb(fill) if isinstance(fill, str) else tuple(fill)[:3]
    dest = draw._image
    k = 4
    layer = Image.new("L", (dest.width * k, dest.height * k), 0)
    ld = ImageDraw.Draw(layer)
    width_px = max(3, int(amplitude * 0.5)) * k
    steps = 400
    for i in range(lines):
        yy = y + i * spacing
        pts = []
        for s in range(steps + 1):
            t = s / steps
            px = x0 + t * w
            py = yy + math.sin(t * 3.14159 * 2.4 + i) * amplitude
            pts.append((px * k, py * k))
        ld.line(pts, fill=255, width=width_px, joint="curve")
        r = width_px / 2
        for (cx, cy) in (pts[0], pts[-1]):          # round caps
            ld.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    _composite(dest, layer.resize(dest.size, Image.LANCZOS), rgb)


def render_icon_mark(size=1024, out_path="icon_mark.png", background=None):
    """
    Standalone square icon: sun rising behind Table Mountain, waves at the
    base. No text -- for a profile picture / app-icon candidate. Pass
    background=None for a transparent PNG, or a hex colour / (top, bottom)
    tuple for a filled gradient tile.
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if background is not None:
        top_hex, bottom_hex = background if isinstance(background, tuple) else (background, background)
        top, bottom = _hex_to_rgb(top_hex), _hex_to_rgb(bottom_hex)
        for yy in range(size):
            t = yy / size
            r = int(top[0] + (bottom[0] - top[0]) * t)
            g = int(top[1] + (bottom[1] - top[1]) * t)
            b = int(top[2] + (bottom[2] - top[2]) * t)
            draw.line([(0, yy), (size, yy)], fill=(r, g, b, 255))

    horizon = size * 0.66
    mountain_fill = tuple(int(c * 0.55) for c in _hex_to_rgb(TEAL_DEEP))   # darker than the sea so it reads
    draw_sun(draw, size * 0.5, size * 0.23, size * 0.10, fill=YELLOW, rays=True, upper_only=True)
    draw_mountain(draw, 0, horizon, size, size * 0.30, fill=mountain_fill, simple=True)
    draw.rectangle((0, horizon, size, size), fill=mountain_fill + (255,) if img.mode == "RGBA" else mountain_fill)
    draw_waves(draw, 0, horizon + size * 0.06, size, amplitude=size * 0.018, fill=WHITE, lines=3, spacing=size * 0.045)

    img.save(out_path, "PNG")
    return out_path


def render_app_icon(size=1024, out_path="app_icon.png"):
    """Full-bleed square, no transparency, no text -- ready to drop into
    an Xcode asset catalog or use as an Instagram profile picture."""
    return render_icon_mark(size=size, out_path=out_path, background=(TEAL_BRIGHT, TEAL_DEEP))


def draw_wordmark_lockup(draw: ImageDraw.ImageDraw, cx, y, scale=1.0,
                          text_color=None, mountain_color=None, sun_color=None):
    """
    Draws the icon + script wordmark side by side, centred on cx, top at y.
    Used inline in post footers (image_gen.py) so every post carries the
    same mark, not just the words.
    """
    text_color = text_color or INK
    mountain_color = mountain_color or (text_color)
    sun_color = sun_color or YELLOW

    font = ImageFont.truetype(F_SCRIPT, int(88 * scale))
    text = "Beach, Please!"
    text_w = draw.textlength(text, font=font)
    icon_size = int(96 * scale)
    gap = int(18 * scale)
    total_w = icon_size + gap + text_w

    icon_x0 = cx - total_w / 2
    text_x = icon_x0 + icon_size + gap

    # small icon: sun + mountain, no waves (too fine at this size)
    sun_cx = icon_x0 + icon_size * 0.5
    sun_cy = y + icon_size * 0.17
    draw_sun(draw, sun_cx, sun_cy, icon_size * 0.13, fill=sun_color, rays=False)
    draw_mountain(draw, icon_x0, y + icon_size, icon_size, icon_size * 0.62, fill=mountain_color, simple=True)

    draw.text((text_x, y - int(6 * scale)), text, font=font, fill=_hex_to_rgb(text_color) if isinstance(text_color, str) else text_color)
    return total_w


def render_lockup_asset(out_path="logo_lockup.png", width=1600, height=420,
                         background=None, text_color=INK, sun_color=YELLOW):
    """Standalone horizontal logo file (icon + script wordmark) for use
    outside the posts -- a website header, bio link, etc. background=None
    gives a transparent PNG."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if background is not None:
        draw.rectangle((0, 0, width, height), fill=_hex_to_rgb(background) + (255,) if isinstance(background, str) else background)
    scale = height / 300
    draw_wordmark_lockup(draw, cx=width / 2, y=height * 0.28, scale=scale,
                          text_color=text_color, sun_color=sun_color)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    render_icon_mark(1024, "icon_transparent.png", background=None)
    render_app_icon(1024, "app_icon.png")
    render_icon_mark(1024, "icon_pink.png", background=(PINK, TEAL_DEEP))
    render_lockup_asset("logo_lockup_transparent.png", background=None, text_color=TEAL_DEEP)
    render_lockup_asset("logo_lockup_cream.png", background=CREAM, text_color=TEAL_DEEP)
