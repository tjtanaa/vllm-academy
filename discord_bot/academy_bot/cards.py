"""Image cards rendered with Pillow: episode covers, profile cards, KV budgets, banners.

Visual language: deep-ink background, a grid of "KV blocks" (the PagedAttention motif)
tinted with the season color, heavy display type, numbers highlighted like a thumbnail.
"""
from __future__ import annotations

import io
import os
import random
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

INK_TOP = (7, 11, 20)
INK_BOTTOM = (16, 22, 40)
WHITE = (245, 247, 255)
MUTED = (148, 163, 196)
SOFT = (199, 210, 254)
BRAND = (253, 186, 52)  # vLLM-ish amber
BLUE = (59, 130, 246)
RED = (239, 68, 68)
GREEN = (52, 211, 153)

_FONT_DIRS = [
    os.getenv("ACADEMY_FONT_DIR", ""),
    str(Path(__file__).resolve().parents[2] / "academy" / "assets" / "fonts"),
    "/usr/share/fonts/opentype/noto",
    "/usr/share/fonts/opentype/noto-cjk",
    "/usr/share/fonts/noto-cjk",
    "/usr/share/fonts/google-noto-cjk",
    "/System/Library/Fonts",
    "/Library/Fonts",
    "C:/Windows/Fonts",
]
_FONT_FILES = {
    "black": ["NotoSansCJK-Black.ttc", "NotoSansCJKtc-Black.otf", "NotoSansTC-Black.otf", "NotoSansCJK-Bold.ttc",
              "NotoSansCJKtc-Bold.otf", "NotoSansTC-Bold.otf", "PingFang.ttc", "msjhbd.ttc"],
    "bold": ["NotoSansCJK-Bold.ttc", "NotoSansCJKtc-Bold.otf", "NotoSansTC-Bold.otf", "PingFang.ttc", "msjhbd.ttc"],
    "regular": ["NotoSansCJK-Regular.ttc", "NotoSansCJKtc-Regular.otf", "NotoSansTC-Regular.otf", "PingFang.ttc",
                "msjh.ttc"],
    "mono": ["DejaVuSansMono-Bold.ttf", "LiberationMono-Bold.ttf", "Menlo.ttc", "consolab.ttf"],
}
_MONO_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/dejavu"]


def _tc_index(path: str) -> int:
    """Pick the Traditional Chinese face inside a CJK .ttc collection."""
    if not path.endswith(".ttc"):
        return 0
    for i in range(10):
        try:
            name = ImageFont.truetype(path, 12, index=i).getname()[0]
        except OSError:
            break
        if name.endswith(" TC") or "TC" in name.split():
            return i
    return 0


@lru_cache(maxsize=64)
def font(weight: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    dirs = _MONO_DIRS + _FONT_DIRS if weight == "mono" else _FONT_DIRS
    for d in dirs:
        if not d:
            continue
        for name in _FONT_FILES[weight]:
            p = Path(d) / name
            if p.exists():
                try:
                    return ImageFont.truetype(str(p), size, index=_tc_index(str(p)))
                except OSError:
                    continue
    if weight != "regular":
        return font("regular", size)
    return ImageFont.load_default(size)


def has_cjk_font() -> bool:
    return isinstance(font("regular", 20), ImageFont.FreeTypeFont)


def _rgb(color: int | tuple[int, int, int]) -> tuple[int, int, int]:
    if isinstance(color, tuple):
        return color
    return ((color >> 16) & 255, (color >> 8) & 255, color & 255)


def _mix(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _background(w: int, h: int) -> Image.Image:
    img = Image.new("RGB", (w, h), INK_TOP)
    px = ImageDraw.Draw(img)
    for y in range(h):
        px.line([(0, y), (w, y)], fill=_mix(INK_TOP, INK_BOTTOM, y / max(1, h - 1)))
    return img


def _glow(img: Image.Image, center: tuple[int, int], radius: int, color, strength: int = 90) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, y = center
    d.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*color, strength))
    layer = layer.filter(ImageFilter.GaussianBlur(radius // 2))
    img.paste(layer, (0, 0), layer)


def _block_grid(img: Image.Image, box: tuple[int, int, int, int], color, seed: int, cell: int = 34, gap: int = 9) -> None:
    """The PagedAttention motif: a grid of KV blocks, some allocated, some shared, some free."""
    rnd = random.Random(seed)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    cols = (x1 - x0) // (cell + gap)
    rows = (y1 - y0) // (cell + gap)
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cell + gap)
            y = y0 + r * (cell + gap)
            fade = 0.35 + 0.65 * (c / max(1, cols - 1))  # brighter towards the right edge
            roll = rnd.random()
            if roll < 0.30:
                a = int(210 * fade)
                d.rounded_rectangle([x, y, x + cell, y + cell], radius=7, fill=(*color, a))
            elif roll < 0.42:
                a = int(150 * fade)
                d.rounded_rectangle([x, y, x + cell, y + cell], radius=7, fill=(*SOFT, int(a * 0.55)))
            else:
                d.rounded_rectangle([x, y, x + cell, y + cell], radius=7, outline=(*MUTED, int(70 * fade)), width=2)
    img.paste(layer, (0, 0), layer)


def _wrap(draw: ImageDraw.ImageDraw, text: str, fnt, max_w: int) -> list[str]:
    """Wrap Latin text on spaces and CJK text per character."""
    tokens = re.findall(r"[A-Za-z0-9×%$.,:;!?'\"()\-+/<>=#@&]+|\s+|.", text)
    lines, cur = [], ""
    for tok in tokens:
        trial = cur + tok
        if draw.textlength(trial, font=fnt) <= max_w or not cur.strip():
            cur = trial
        else:
            lines.append(cur.rstrip())
            cur = tok.lstrip()
    if cur.strip():
        lines.append(cur.rstrip())
    return lines


def _fit_lines(draw, text, weight, sizes, max_w, max_lines):
    for size in sizes:
        f = font(weight, size)
        lines = _wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
    f = font(weight, sizes[-1])
    lines = _wrap(draw, text, f, max_w)[:max_lines]
    if lines:
        lines[-1] = lines[-1].rstrip(" .,") + "…"
    return f, lines


def _draw_highlighted(draw, xy, line, fnt, base, accent) -> None:
    """Draw a line, coloring number-ish tokens (24×, 90%, 130, 1960s) in the accent color."""
    x, y = xy
    for part in re.split(r"(\d[\d,.]*\s?[×x%]?|\d+s)", line):
        if not part:
            continue
        color = accent if re.match(r"\d", part) else base
        draw.text((x, y), part, font=fnt, fill=color)
        x += draw.textlength(part, font=fnt)


def _pill(draw, xy, text, fnt, fg, bg, pad=(18, 9)) -> int:
    x, y = xy
    w = draw.textlength(text, font=fnt)
    h = fnt.size if hasattr(fnt, "size") else 16
    draw.rounded_rectangle([x, y, x + w + 2 * pad[0], y + h + 2 * pad[1] + 4], radius=(h + 2 * pad[1]) // 2, fill=bg)
    draw.text((x + pad[0], y + pad[1] - 2), text, font=fnt, fill=fg)
    return int(x + w + 2 * pad[0])


def _png(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# --------------------------------------------------------------------------- episode cover
def episode_cover(*, ep_id: str, title_en: str, title_zh: str, season_label_en: str, season_label_zh: str,
                  color: int, minutes: int, xp: int) -> bytes:
    W, H = 1200, 630
    accent = _rgb(color)
    img = _background(W, H)
    _glow(img, (1010, 120), 260, accent, 70)
    _glow(img, (120, 620), 220, BLUE, 40)
    _block_grid(img, (700, 40, 1180, 560), accent, seed=int(re.sub(r"\D", "", ep_id) or 0) * 7919)
    # fade the grid under the text column
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for x in range(700, 900):
        a = int(200 * (1 - (x - 700) / 200))
        sd.line([(x, 0), (x, H)], fill=(*INK_TOP, a))
    img.paste(shade, (0, 0), shade)
    d = ImageDraw.Draw(img)

    _pill(d, (64, 56), f"{season_label_en.upper()}  ·  {season_label_zh}", font("bold", 22), INK_TOP, accent)
    d.text((60, 104), ep_id, font=font("black", 132), fill=accent)

    # shrink the EN title until EN + ZH both fit above the footer
    limit = H - 72 - 16
    en_sizes, zh_sizes = [62, 56, 50, 44, 40, 36], [40, 36, 32, 28]
    for i in range(len(en_sizes)):
        f_en, en_lines = _fit_lines(d, title_en, "black", en_sizes[i:], 760, 3)
        f_zh, zh_lines = _fit_lines(d, title_zh, "bold", zh_sizes[min(i, len(zh_sizes) - 1):], 780, 2)
        total = len(en_lines) * int(f_en.size * 1.16) + 10 + len(zh_lines) * int(f_zh.size * 1.25)
        if 268 + total <= limit:
            break
    y = 268
    for line in en_lines:
        _draw_highlighted(d, (64, y), line, f_en, WHITE, accent)
        y += int(f_en.size * 1.16)
    y += 10
    for line in zh_lines:
        _draw_highlighted(d, (64, y), line, f_zh, SOFT, accent)
        y += int(f_zh.size * 1.25)

    # footer
    d.rectangle([0, H - 72, W, H], fill=(5, 8, 15))
    d.rectangle([0, H - 72, W, H - 69], fill=accent)
    d.text((64, H - 54), "vLLM ACADEMY", font=font("black", 30), fill=WHITE)
    tail = f"{minutes} MIN  ·  +{xp} XP  ·  EN / 繁中"
    ft = font("bold", 24)
    d.text((W - 64 - d.textlength(tail, font=ft), H - 50), tail, font=ft, fill=MUTED)
    return _png(img)


# --------------------------------------------------------------------------- banner
def banner(*, title: str = "vLLM ACADEMY", subtitle_zh: str = "從零到推論工程師",
           subtitle_en: str = "Zero to Inference Engineer", color: int = 0xFDBA34) -> bytes:
    W, H = 1200, 420
    accent = _rgb(color)
    img = _background(W, H)
    _glow(img, (980, 80), 260, accent, 80)
    _glow(img, (200, 420), 240, BLUE, 50)
    _block_grid(img, (690, 30, 1180, 400), accent, seed=2026, cell=30, gap=8)
    d = ImageDraw.Draw(img)
    _pill(d, (64, 60), "vLLM TAIWAN COMMUNITY · 台灣社群", font("bold", 22), INK_TOP, accent)
    d.text((60, 110), title, font=font("black", 104), fill=WHITE)
    d.text((64, 248), subtitle_zh, font=font("black", 50), fill=accent)
    d.text((66, 318), subtitle_en, font=font("bold", 34), fill=SOFT)
    return _png(img)


# --------------------------------------------------------------------------- profile
def profile_card(*, name: str, avatar: bytes | None, level: int, rank_en: str, rank_zh: str, xp: int,
                 to_next: int, progress: float, streak: int, position: int, badges: list[str],
                 seasons: list[tuple[str, int, int, int]], color: int = 0xFDBA34) -> bytes:
    """seasons: list of (label, done, total, color)."""
    W, H = 1100, 420
    accent = _rgb(color)
    img = _background(W, H)
    _glow(img, (170, 170), 200, accent, 70)
    d = ImageDraw.Draw(img)
    # avatar
    size = 200
    ax, ay = 60, 60
    if avatar:
        try:
            av = Image.open(io.BytesIO(avatar)).convert("RGB").resize((size, size))
        except Exception:  # noqa: BLE001 — any bad image falls back to initials
            av = None
    else:
        av = None
    if av is None:
        av = Image.new("RGB", (size, size), _mix(INK_BOTTOM, accent, 0.35))
        ad = ImageDraw.Draw(av)
        initial = (name.strip() or "?")[0].upper()
        f = font("black", 96)
        ad.text(((size - ad.textlength(initial, font=f)) / 2, 36), initial, font=f, fill=WHITE)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    d.ellipse([ax - 8, ay - 8, ax + size + 8, ay + size + 8], outline=accent, width=6)
    img.paste(av, (ax, ay), mask)
    _pill(d, (ax + 34, ay + size + 20), f"LV.{level}", font("black", 30), INK_TOP, accent, pad=(22, 8))

    # name + rank
    x = 320
    f_name, name_lines = _fit_lines(d, name, "black", [58, 50, 44, 38], 740, 1)
    d.text((x, 52), name_lines[0] if name_lines else name, font=f_name, fill=WHITE)
    d.text((x, 128), f"{rank_en}  ·  {rank_zh}", font=font("bold", 32), fill=accent)
    # xp bar
    bx0, by0, bx1, by1 = x, 190, W - 60, 222
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=(30, 38, 62))
    fill_w = int((bx1 - bx0) * max(0.02, progress))
    bar = Image.new("RGB", (max(1, fill_w), by1 - by0))
    bd = ImageDraw.Draw(bar)
    for i in range(fill_w):
        bd.line([(i, 0), (i, by1 - by0)], fill=_mix(accent, WHITE, 0.35 * i / max(1, fill_w)))
    bmask = Image.new("L", bar.size, 0)
    ImageDraw.Draw(bmask).rounded_rectangle([0, 0, bar.size[0] - 1, bar.size[1] - 1], radius=16, fill=255)
    img.paste(bar, (bx0, by0), bmask)
    stats = f"{xp:,} XP" + (f"   ·   {to_next:,} to next" if to_next else "   ·   MAX RANK")
    d.text((x, 234), stats, font=font("bold", 26), fill=SOFT)
    right = f"#{position}   ·   STREAK {streak}d"
    fr = font("bold", 26)
    d.text((bx1 - d.textlength(right, font=fr), 234), right, font=fr, fill=MUTED)

    # season progress
    sx, sy = x, 290
    n = max(1, min(len(seasons), 8))
    seg_w = (W - 60 - x - (n - 1) * 14) // n
    fl = font("bold", 20 if n <= 6 else 17)
    for i, (label, done, total, scol) in enumerate(seasons[:n]):
        cx = sx + i * (seg_w + 14)
        d.text((cx, sy), f"{label}  {done}/{total}", font=fl, fill=MUTED)
        d.rounded_rectangle([cx, sy + 30, cx + seg_w, sy + 42], radius=6, fill=(30, 38, 62))
        if total:
            d.rounded_rectangle([cx, sy + 30, cx + max(8, int(seg_w * done / total)), sy + 42], radius=6,
                                fill=_rgb(scol) if done else (30, 38, 62))
    # badges
    fx = 60
    fb = font("bold", 20)
    for b in badges[:7]:
        w = d.textlength(b, font=fb) + 28
        if fx + w > W - 40:
            break
        d.rounded_rectangle([fx, H - 56, fx + w, H - 22], radius=17, outline=accent, width=2)
        d.text((fx + 14, H - 52), b, font=fb, fill=WHITE)
        fx += w + 10
    if not badges:
        d.text((60, H - 52), "No badges yet: /episode E01", font=fb, fill=MUTED)
    return _png(img)


# --------------------------------------------------------------------------- kv budget
def kv_card(*, model: str, subtitle: str, per_token: str, per_seq: str, max_seqs: int, weights_gib: float,
            kv_gib: float, budget_gib: float, fits: bool) -> bytes:
    W, H = 1100, 440
    img = _background(W, H)
    accent = BRAND if fits else RED
    _glow(img, (1000, 60), 220, accent, 60)
    d = ImageDraw.Draw(img)
    d.text((56, 40), model, font=font("black", 50), fill=WHITE)
    d.text((58, 104), subtitle, font=font("bold", 26), fill=MUTED)
    cols = [("KV / TOKEN", per_token), ("KV / SEQUENCE", per_seq), ("MAX SEQUENCES", str(max_seqs))]
    cw = (W - 112) // 3
    for i, (label, value) in enumerate(cols):
        cx = 56 + i * cw
        d.text((cx, 160), label, font=font("bold", 22), fill=MUTED)
        d.text((cx, 190), value, font=font("black", 56), fill=accent if i == 2 else WHITE)
    # stacked memory bar
    bx0, by0, bx1, by1 = 56, 300, W - 56, 350
    total = max(budget_gib, weights_gib + kv_gib, 1e-9)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=12, fill=(30, 38, 62))
    width = bx1 - bx0
    w_px = int(width * min(weights_gib, total) / total)
    kv_px = int(width * min(kv_gib, max(0.0, total - weights_gib)) / total)
    d.rounded_rectangle([bx0, by0, bx0 + max(w_px, 4), by1], radius=12, fill=(96, 112, 160))
    kv_color = BRAND if fits else RED
    if kv_px > 0:
        d.rectangle([bx0 + w_px, by0, bx0 + w_px + kv_px, by1], fill=kv_color)
    if budget_gib < total:  # overflow marker at budget line
        bxm = bx0 + int(width * budget_gib / total)
        d.line([(bxm, by0 - 12), (bxm, by1 + 12)], fill=WHITE, width=4)
    fl = font("bold", 22)
    legend = [((96, 112, 160), f"weights {weights_gib:.0f} GiB"), (kv_color, f"KV {kv_gib:.0f} GiB"),
              ((30, 38, 62), f"budget {budget_gib:.0f} GiB")]
    lx = 56
    for col, text in legend:
        d.rounded_rectangle([lx, 372, lx + 22, 394], radius=5, fill=col, outline=MUTED if col == (30, 38, 62) else None)
        d.text((lx + 32, 370), text, font=fl, fill=SOFT)
        lx += 52 + int(d.textlength(text, font=fl))
    tag = "FITS" if fits else "OOM"
    ft = font("black", 30)
    _pill(d, (W - 56 - int(d.textlength(tag, font=ft)) - 44, 44), tag, ft, INK_TOP, accent)
    return _png(img)


# --------------------------------------------------------------------------- hot take
VERDICT_COLORS = {"right": GREEN, "wrong": RED, "partly": BRAND}


def hottake_card(*, take_id: str, claim_en: str, claim_zh: str, confidence: int, judge_on: str,
                 agree: int = 0, disagree: int = 0, verdict: str | None = None, color: int = 0xEF4444) -> bytes:
    """A shareable 'Hot Take Court' card: the claim, our confidence, the judge date and the room's vote split."""
    W, H = 1200, 630
    accent = _rgb(color)
    img = _background(W, H)
    _glow(img, (1060, 90), 260, accent, 70)
    _glow(img, (140, 640), 240, (168, 85, 247), 45)
    _block_grid(img, (900, 36, 1180, 300), accent, seed=sum(map(ord, take_id)) * 131, cell=26, gap=8)
    d = ImageDraw.Draw(img)
    _pill(d, (64, 48), "HOT TAKE COURT  ·  大膽預測  ·  SPECULATION", font("bold", 22), INK_TOP, accent)
    my = 446  # meters row
    en_sizes, zh_sizes = [50, 46, 42, 38, 34, 30], [32, 30, 28, 26, 24]
    for i in range(len(en_sizes)):
        f_en, en_lines = _fit_lines(d, claim_en, "black", en_sizes[i:], 800, 4)
        f_zh, zh_lines = _fit_lines(d, claim_zh, "bold", zh_sizes[min(i, len(zh_sizes) - 1):], 820, 2)
        total = len(en_lines) * int(f_en.size * 1.18) + 12 + len(zh_lines) * int(f_zh.size * 1.32)
        if 112 + total <= my - 20:
            break
    y = 112
    for line in en_lines:
        _draw_highlighted(d, (64, y), line, f_en, WHITE, accent)
        y += int(f_en.size * 1.18)
    y += 12
    for line in zh_lines:
        d.text((64, y), line, font=f_zh, fill=SOFT)
        y += int(f_zh.size * 1.32)

    # confidence meter
    d.text((64, my), "OUR CONFIDENCE · 信心", font=font("bold", 22), fill=MUTED)
    bx0, by0, bx1, by1 = 64, my + 36, 600, my + 66
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=15, fill=(30, 38, 62))
    fill = int((bx1 - bx0) * max(0.02, min(1.0, confidence / 100)))
    d.rounded_rectangle([bx0, by0, bx0 + fill, by1], radius=15, fill=accent)
    d.text((bx1 + 20, my + 22), f"{confidence}%", font=font("black", 50), fill=WHITE)

    # vote split
    total = agree + disagree
    vx0, vx1 = 760, W - 64
    d.text((vx0, my), "THE ROOM · 大家怎麼看", font=font("bold", 22), fill=MUTED)
    d.rounded_rectangle([vx0, by0, vx1, by1], radius=15, fill=(30, 38, 62))
    if total:
        aw = int((vx1 - vx0) * agree / total)
        if aw > 0:
            d.rounded_rectangle([vx0, by0, vx0 + max(aw, 30), by1], radius=15, fill=BRAND)
        if agree < total:
            d.rounded_rectangle([vx0 + aw, by0, vx1, by1], radius=15, fill=BLUE)
        txt = f"AGREE {agree}  ·  {disagree} DISAGREE"
    else:
        txt = "No votes yet: be the first"
    d.text((vx0, by1 + 12), txt, font=font("bold", 22), fill=SOFT)

    # verdict stamp
    if verdict in VERDICT_COLORS:
        vc = VERDICT_COLORS[verdict]
        label = {"right": "CALLED IT", "wrong": "WE WERE WRONG", "partly": "PARTLY RIGHT"}[verdict]
        stamp = Image.new("RGBA", (520, 120), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rounded_rectangle([4, 4, 516, 116], radius=18, outline=(*vc, 235), width=8)
        fs = font("black", 52)
        sd.text(((520 - sd.textlength(label, font=fs)) / 2, 26), label, font=fs, fill=(*vc, 235))
        stamp = stamp.rotate(-9, expand=True, resample=Image.BICUBIC)
        img.paste(stamp, (W - stamp.width - 30, 250), stamp)
        d = ImageDraw.Draw(img)

    # footer
    d.rectangle([0, H - 72, W, H], fill=(5, 8, 15))
    d.rectangle([0, H - 72, W, H - 69], fill=accent)
    d.text((64, H - 54), "vLLM ACADEMY", font=font("black", 30), fill=WHITE)
    tail = f"{take_id.upper()}  ·  JUDGED ON {judge_on}  ·  /hottake"
    ft = font("bold", 24)
    d.text((W - 64 - d.textlength(tail, font=ft), H - 50), tail, font=ft, fill=MUTED)
    return _png(img)
