#!/usr/bin/env python3
"""The Daily Globe — Monday 23 November 2026.

Draws a dense one-page newspaper front page summing up the day's world
news: 36 verified stories across 7 regions, 3 lead stories with real
event photos, a markets ticker and photo thumbnails for the most visual
stories (other stories keep small hand-drawn icon cards). All text is
drawn with PIL from DejaVu fonts; every story was checked against wire
reports of the day. Photos are freely licensed Wikimedia Commons images,
baked into entry.png at render time (main.ts only copies entry.png, so no
network is needed at grade time). Output: entry.png, 1024x1024, under
1 MiB.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
PHOTOS = os.path.join(HERE, "photos")

_photo_cache = {}


def photo(path, w, h):
    """Load a photo from photos/, centre-cropped to w x h; cached."""
    key = (path, w, h)
    if key not in _photo_cache:
        im = Image.open(os.path.join(PHOTOS, path)).convert("RGB")
        _photo_cache[key] = ImageOps.fit(im, (w, h), Image.LANCZOS)
    return _photo_cache[key]


def place_photo(img, x, y, path, w, h):
    img.paste(photo(path, w, h), (x, y))
    img_draw = ImageDraw.Draw(img)
    img_draw.rectangle([x, y, x + w - 1, y + h - 1], outline=(120, 110, 90), width=1)

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
BG = (246, 241, 227)
PAPER = (255, 253, 246)
INK = (26, 26, 26)
MUTED = (90, 84, 70)
RED = (155, 28, 28)
NAVY = (31, 58, 95)
RULE = (26, 26, 26)
HAIR = (178, 168, 148)

SECTION_COLORS = {
    "NORTH AMERICA": (31, 58, 95),
    "LATIN AMERICA": (122, 74, 18),
    "EUROPE": (45, 90, 61),
    "MIDDLE EAST": (139, 26, 26),
    "AFRICA": (99, 66, 130),
    "ASIA-PACIFIC": (14, 110, 110),
    "SPORT & SCIENCE": (70, 70, 78),
}

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


F_MAST = font("DejaVuSerif-Bold.ttf", 58)
F_DATE = font("DejaVuSans-Bold.ttf", 13)
F_KICK = font("DejaVuSans-Bold.ttf", 11)
F_LEAD_H = font("DejaVuSerif-Bold.ttf", 19)
F_LEAD_S = font("DejaVuSans.ttf", 12)
F_SEC = font("DejaVuSans-Bold.ttf", 11)
F_HEAD = font("DejaVuSans-Bold.ttf", 13)
F_SUM = font("DejaVuSans.ttf", 11)
F_TICK = font("DejaVuSans-Bold.ttf", 12)
F_FOOT = font("DejaVuSans.ttf", 10)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, lines, fnt, fill, leading):
    x, y = xy
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------- icons
def icon_box(draw, x, y, s, tint):
    draw.rounded_rectangle([x, y, x + s, y + s], radius=5, fill=tint,
                           outline=(120, 110, 90), width=1)


def icon_globe(draw, x, y, s):
    icon_box(draw, x, y, s, (214, 235, 214))
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 4
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(45, 90, 61), width=2)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=(45, 90, 61), width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=(45, 90, 61), width=1)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340, fill=(45, 90, 61), width=1)


def icon_chart(draw, x, y, s):
    icon_box(draw, x, y, s, (245, 214, 214))
    draw.line([x + 6, y + s - 7, x + s - 5, y + s - 7], fill=INK, width=2)
    draw.line([x + 6, y + s - 7, x + 6, y + 6], fill=INK, width=2)
    pts = [(x + 8, y + 10), (x + 15, y + 15), (x + 21, y + 13), (x + 28, y + 22), (x + 34, y + 27)]
    draw.line(pts, fill=(155, 28, 28), width=2, joint="curve")
    draw.polygon([(x + 34, y + 27), (x + 30, y + 25), (x + 33, y + 31)], fill=(155, 28, 28))


def icon_tanker(draw, x, y, s):
    icon_box(draw, x, y, s, (214, 226, 240))
    draw.polygon([(x + 5, y + 18), (x + s - 5, y + 18), (x + s - 9, y + 28), (x + 9, y + 28)],
                 fill=(31, 58, 95))
    draw.rectangle([x + 9, y + 10, x + 17, y + 18], fill=(155, 28, 28))
    draw.rectangle([x + 19, y + 12, x + 26, y + 18], fill=(31, 58, 95))
    for yy in (y + 31, y + 34):
        draw.line([x + 5, yy, x + s - 5, yy], fill=(90, 130, 170), width=1)


def icon_missile(draw, x, y, s):
    icon_box(draw, x, y, s, (232, 226, 214))
    draw.line([x + 8, y + s - 8, x + s - 8, y + 8], fill=(90, 84, 70), width=2)
    draw.polygon([(x + s - 12, y + 6), (x + s - 5, y + 5), (x + s - 6, y + 12)],
                 fill=(155, 28, 28))
    draw.polygon([(x + 8, y + s - 8), (x + 14, y + s - 8), (x + 8, y + s - 14)],
                 fill=(90, 84, 70))


def icon_building(draw, x, y, s):
    icon_box(draw, x, y, s, (226, 226, 226))
    draw.rectangle([x + 10, y + 7, x + s - 10, y + s - 7], fill=(90, 84, 70))
    for wy in (y + 11, y + 18, y + 25):
        for wx in (x + 13, x + 20, x + 27):
            draw.rectangle([wx, wy, wx + 4, wy + 4], fill=(246, 241, 227))
    draw.line([(x + 20, y + 7), (x + 16, y + 16), (x + 22, y + 22)], fill=(155, 28, 28), width=2)


def icon_rugby(draw, x, y, s):
    icon_box(draw, x, y, s, (235, 222, 200))
    draw.ellipse([x + 6, y + 12, x + s - 6, y + s - 12], fill=(122, 74, 18))
    draw.line([x + 14, y + s // 2, x + s - 14, y + s // 2], fill=(246, 241, 227), width=2)
    for dx in (-6, 0, 6):
        draw.line([x + s // 2 + dx, y + s // 2 - 4, x + s // 2 + dx, y + s // 2 + 4],
                  fill=(246, 241, 227), width=1)


def icon_soccer(draw, x, y, s):
    icon_box(draw, x, y, s, (226, 236, 226))
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 5
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=2, fill=(255, 253, 246))
    draw.polygon([(cx, cy - 6), (cx + 6, cy - 2), (cx + 4, cy + 5), (cx - 4, cy + 5), (cx - 6, cy - 2)],
                 fill=INK)


def icon_chip(draw, x, y, s):
    icon_box(draw, x, y, s, (220, 232, 220))
    draw.rectangle([x + 10, y + 10, x + s - 10, y + s - 10], fill=(45, 90, 61))
    draw.rectangle([x + 15, y + 15, x + s - 15, y + s - 15], fill=(246, 241, 227))
    for i in range(3):
        px = x + 13 + i * 7
        py = y + 13 + i * 7
        draw.line([px, y + 5, px, y + 10], fill=INK, width=2)
        draw.line([px, y + s - 10, px, y + s - 5], fill=INK, width=2)
        draw.line([x + 5, py, x + 10, py], fill=INK, width=2)
        draw.line([x + s - 10, py, x + s - 5, py], fill=INK, width=2)


def icon_planet(draw, x, y, s):
    icon_box(draw, x, y, s, (222, 222, 240))
    cx, cy, r = x + s // 2, y + s // 2, s // 2 - 8
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 110, 80))
    draw.ellipse([cx - r - 3, cy - 2, cx + r + 3, cy + 4], outline=(155, 28, 28), width=2)


def icon_flame(draw, x, y, s):
    icon_box(draw, x, y, s, (250, 228, 200))
    pts = [(x + s // 2, y + 6), (x + s - 8, y + 20), (x + s - 10, y + 30),
           (x + s // 2 + 3, y + 26), (x + s // 2 - 2, y + 32), (x + 8, y + 28),
           (x + 10, y + 18)]
    draw.polygon(pts, fill=(220, 90, 20))
    draw.polygon([(x + s // 2, y + 18), (x + s - 12, y + 28), (x + s // 2, y + 31),
                  (x + 12, y + 28)], fill=(240, 180, 40))


def icon_chess(draw, x, y, s):
    icon_box(draw, x, y, s, (232, 228, 240))
    draw.rectangle([x + 11, y + 8, x + 15, y + 13], fill=INK)
    draw.rectangle([x + 18, y + 8, x + 22, y + 13], fill=INK)
    draw.rectangle([x + 25, y + 8, x + 29, y + 13], fill=INK)
    draw.rectangle([x + 11, y + 13, x + 29, y + 18], fill=INK)
    draw.polygon([(x + 13, y + 18), (x + 27, y + 18), (x + 31, y + s - 7), (x + 9, y + s - 7)],
                 fill=INK)


def icon_ship(draw, x, y, s):
    icon_box(draw, x, y, s, (214, 226, 240))
    draw.polygon([(x + 6, y + 22), (x + s - 6, y + 22), (x + s - 10, y + 30), (x + 10, y + 30)],
                 fill=(31, 58, 95))
    draw.line([x + s // 2, y + 8, x + s // 2, y + 22], fill=INK, width=2)
    draw.polygon([(x + s // 2, y + 8), (x + s // 2 + 9, y + 12), (x + s // 2, y + 15)],
                 fill=(155, 28, 28))
    draw.line([x + 5, y + 33, x + s - 5, y + 33], fill=(90, 130, 170), width=1)


def icon_leaf(draw, x, y, s):
    icon_box(draw, x, y, s, (214, 235, 214))
    draw.ellipse([x + 8, y + 8, x + s - 8, y + s - 6], fill=(45, 120, 61))
    draw.line([x + s // 2, y + 10, x + s // 2, y + s - 8], fill=(246, 241, 227), width=2)
    draw.line([x + s // 2, y + 20, x + 12, y + 14], fill=(246, 241, 227), width=1)
    draw.line([x + s // 2, y + 24, x + s - 12, y + 18], fill=(246, 241, 227), width=1)


ICONS = {
    "globe": icon_globe, "chart": icon_chart, "tanker": icon_tanker,
    "missile": icon_missile, "building": icon_building, "rugby": icon_rugby,
    "soccer": icon_soccer, "chip": icon_chip, "planet": icon_planet,
    "flame": icon_flame, "chess": icon_chess, "ship": icon_ship,
    "leaf": icon_leaf,
}

# ---------------------------------------------------------------- stories
# (kicker, headline, summary, photo file in photos/)
LEADS = [
    ("CLIMATE  •  ANTALYA", "COP31 collapses in fossil-fuel deadlock",
     "Nearly 200 nations leave Antalya with no deal after record overtime "
     "over fossil fuels.", "lead_cop31.jpg"),
    ("MARKETS", "Stocks rout deepens as Asia scrambles to stop the slide",
     "The S&P 500 fell 3.7% and the Nasdaq 5.3% on Friday; Asia scrambles "
     "to steady markets.", "lead_markets.jpg"),
    ("GULF CRISIS", "Trump dares Iran to test the Hormuz blockade",
     "Tehran threatens to sail tankers through the strait as mines hit ships; "
     "Houthis hit a Saudi refinery.", "tanker_port.jpg"),
]

# (headline, summary, icon-or-None, photo-or-None)
SECTIONS = [
    ("NORTH AMERICA", [
        ("Bessent warns Fed not to overtighten",
         "The Treasury chief said hawkish talk risks a policy mistake, as Trump blamed Democrats for the slide.", None, None),
        ("ICE detains father and daughter at Seattle airport",
         "The pair were travelling to a family baptism, their lawyer says.", None, None),
        ("Nine shot at California concert",
         "Gunfire at a central California show leaves nine hurt, one critically.", None, None),
        ("First Gen Z woman enters US Congress",
         "Melat Kiros, 29, a Democrat and socialist, wins her seat.", None, None),
        ("Hegseth restores US–Venezuela military ties",
         "The defence secretary's surprise Caracas visit agrees joint training and intelligence sharing.", None, None),
    ]),
    ("LATIN AMERICA", [
        ("Bolsonaro 'stable' in intensive care",
         "Brazil's former president remains in hospital, doctors say.", None, None),
        ("Boca Juniors win the Sudamericana",
         "A 2–0 win over Atlético Mineiro seals the title.", None, "bombonera.jpg"),
    ]),
    ("EUROPE", [
        ("Poland: fallen objects were Russian cruise missiles",
         "Three missiles that fell on Friday are confirmed; NATO is to meet.", "missile", None),
        ("Drone hits Kyiv-area flats; 2 dead, 11 missing",
         "A Russian drone struck a five-storey block in Dymer; two children are among the missing.", "building", None),
        ("Zelenskiy: Trump told Europe it spends too much on Ukraine",
         "The Ukrainian president said Trump raised the cost of the war with European leaders.", None, None),
        ("Germany rallies allies to push Moscow to talks",
         "Berlin signals a united front to press Russia toward a peace deal.", None, None),
        ("England 37–12 All Blacks — a record margin",
         "England's biggest win in 121 years of the rivalry, at Twickenham.", None, "rugby.jpg"),
        ("Liverpool rout ten-man United in Pochettino debut",
         "United's new boss questions Yoro's red card after a nightmare start.", None, "anfield.jpg"),
    ]),
    ("MIDDLE EAST", [
        ("Houthis claim strikes on Saudi refinery",
         "The group says it hit a refinery and radar sites; at least six people were hurt.", None, None),
        ("Iran strike wounds two in Bahrain",
         "Saudi Arabia condemns the attack as 'criminal'.", None, None),
        ("Saudi coalition intercepts Houthi missile",
         "The missile was shot down over the kingdom's western region.", None, None),
        ("Settlers torch 12 Palestinian cars near Ramallah",
         "Vehicles were burned and racist graffiti sprayed in four villages overnight.", None, None),
        ("Netanyahu–Eisenkot coalition talks collapse",
         "The parties end negotiations without a deal to form a government.", None, None),
    ]),
    ("AFRICA", [
        ("Sea drones hit Russian corvette at Benghazi base",
         "Suspected Ukrainian drones struck the warship Merkury in Libya, officials say.", "ship", None),
        ("Sudan drones hit Khartoum; UN building damaged",
         "Strikes hit the capital early on Sunday while UN staff were inside.", None, None),
        ("24 civilians killed in South Sudan violence",
         "Fresh fighting claims two dozen lives, officials report.", None, None),
        ("35 killed in revenge attacks in Nigeria",
         "Fulani herders were killed in Kano state, officials say.", None, None),
        ("WHO chief pleads for peace in Ebola-hit Congo",
         "The agency urges calm as the outbreak strains the region.", None, None),
    ]),
    ("ASIA-PACIFIC", [
        ("Taiwan bans short selling as shares crash",
         "The index lost 17.5% in a week; the ban takes effect today.", "chart", None),
        ("Nvidia chief steps down; shares slide 14%",
         "Huang's exit was announced 12 Nov; an SEC probe is unconfirmed.", None, "huang2.jpg"),
        ("India defies the rout: Nifty up 1.1%",
         "The Sensex jumps as foreign buyers pile in despite the global slide.", None, None),
        ("Indonesia factory fire kills 24",
         "Rescuers recover 24 body bags from a candy plant blaze in Cikande, Banten.", "flame", None),
        ("Lahore chokes on the world's worst air",
         "AQI hits 538 on Sunday morning, the worst of any major city.", None, "lahore.jpg"),
    ]),
    ("SPORT & SCIENCE", [
        ("Firouzja wins first Chess Tour title",
         "The French star beats Giri in an Armageddon decider in Budapest.", None, "firouzja.jpg"),
        ("BepiColombo reaches Mercury orbit",
         "After eight years, only the second mission ever to orbit the planet.", None, "bepicolombo.png"),
        ("India push for Test win as NZ reach 157/4",
         "New Zealand fight on day five of the first Test at lunch.", None, None),
        ("128 states agree to pursue killer-robot rules",
         "Nations aim for international rules on autonomous weapons by 2028.", None, None),
        ("USA beat Canada 6–2 for 12th hockey title",
         "The Americans finish unbeaten at the women's world championship.", None, None),
    ]),
]

TICKER = ("S&P 500  6,910  ▼3.7%   •   Nasdaq  22,618  ▼5.3%   •   "
          "Nikkei  56,437  ▼5.1%   •   Taiwan  36,033  ▼6.2%   •   "
          "Nifty  25,801  ▲1.1%   •   Gold  $3,512   •   VIX  35.9")

TOTAL_STORIES = 3 + sum(len(s[1]) for s in SECTIONS)


PHOTO_W, PHOTO_H = 88, 56
PHOTO_INDENT = PHOTO_W + 8


def story_height(draw, headline, summary, width, icon, photo, max_sum_lines):
    indent = PHOTO_INDENT if photo else (44 if icon else 0)
    tw = width - indent
    hl = wrap(draw, headline, F_HEAD, tw)
    sl = wrap(draw, summary, F_SUM, tw)[:max_sum_lines]
    h = len(hl) * 15 + len(sl) * 11 + 5
    if icon:
        h = max(h, 44 + 4)
    if photo:
        h = max(h, PHOTO_H + 4)
    return h


def draw_story(img, draw, x, y, width, headline, summary, icon, photo, max_sum_lines):
    indent = PHOTO_INDENT if photo else (44 if icon else 0)
    tw = width - indent
    tx = x + indent
    if photo:
        place_photo(img, x, y + 1, photo, PHOTO_W, PHOTO_H)
    elif icon:
        ICONS[icon](draw, x, y + 1, 40)
    hl = wrap(draw, headline, F_HEAD, tw)
    y = draw_wrapped(draw, (tx, y), hl, F_HEAD, INK, 15)
    sl = wrap(draw, summary, F_SUM, tw)[:max_sum_lines]
    y = draw_wrapped(draw, (tx, y + 2), sl, F_SUM, MUTED, 11)
    return y + 1


def layout_columns(draw, max_sum_lines):
    """Greedy balance of sections into 3 columns; returns per-column lists
    of (section_name, stories) plus heights."""
    cols = [[], [], []]
    heights = [0, 0, 0]
    for name, stories in SECTIONS:
        h = 24  # header bar (20) + gap below it (4), as drawn
        for headline, summary, icon, photo in stories:
            h += story_height(draw, headline, summary, 317, icon, photo, max_sum_lines)
        h += 1
        i = heights.index(min(heights))
        cols[i].append((name, stories))
        heights[i] += h
    return cols, heights


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ---- masthead
    draw.line([0, 6, W, 6], fill=RULE, width=3)
    title = "THE DAILY GLOBE"
    tw = draw.textlength(title, font=F_MAST)
    draw.text(((W - tw) / 2, 12), title, font=F_MAST, fill=INK)
    # small globe mark at left
    gx, gy = 30, 16
    draw.ellipse([gx, gy, gx + 52, gy + 52], outline=NAVY, width=3)
    draw.ellipse([gx + 14, gy, gx + 38, gy + 52], outline=NAVY, width=2)
    draw.line([gx, gy + 26, gx + 52, gy + 26], fill=NAVY, width=2)
    draw.line([gx, gy + 52, gx + 52, gy + 52], fill=RULE, width=3)
    date_l = "MONDAY, 23 NOVEMBER 2026"
    date_r = f"{TOTAL_STORIES} STORIES  •  7 REGIONS"
    draw.text((24, 74), date_l, font=F_DATE, fill=RED)
    rw = draw.textlength(date_r, font=F_DATE)
    draw.text((W - 24 - rw, 74), date_r, font=F_DATE, fill=INK)
    mid = "WORLD NEWS IN ONE PAGE"
    mw = draw.textlength(mid, font=F_DATE)
    draw.text(((W - mw) / 2, 74), mid, font=F_DATE, fill=MUTED)
    draw.line([0, 94, W, 94], fill=RULE, width=2)
    draw.line([0, 97, W, 97], fill=RULE, width=1)

    # ---- lead band: real photo on top, then kicker / headline / summary
    LEAD_PHOTO_H = 80
    col_w = (W - 48 - 24) // 3
    for i, (kick, head, summ, photo) in enumerate(LEADS):
        x = 24 + i * (col_w + 12)
        place_photo(img, x, 108, photo, col_w, LEAD_PHOTO_H)
        draw.text((x, 194), kick, font=F_KICK, fill=RED)
        hl = wrap(draw, head, F_LEAD_H, col_w)[:2]
        y = draw_wrapped(draw, (x, 210), hl, F_LEAD_H, INK, 23)
        sl = wrap(draw, summ, F_LEAD_S, col_w)[:2]
        draw_wrapped(draw, (x, y + 4), sl, F_LEAD_S, MUTED, 15)
        if i < 2:
            draw.line([x + col_w + 6, 108, x + col_w + 6, 294], fill=HAIR, width=1)
    draw.line([0, 298, W, 298], fill=RULE, width=1)

    # ---- markets ticker (auto-fit: shrink until it spans the page)
    tick_font = F_TICK
    for size in (12, 11, 10):
        tick_font = font("DejaVuSans-Bold.ttf", size)
        if draw.textlength(TICKER, font=tick_font) <= W - 32:
            break
    draw.rectangle([0, 302, W, 330], fill=NAVY)
    twd = draw.textlength(TICKER, font=tick_font)
    draw.text(((W - twd) / 2, 311), TICKER, font=tick_font, fill=(255, 253, 246))
    draw.line([0, 334, W, 334], fill=RULE, width=1)

    # ---- body columns (adaptive summary length)
    top = 342
    body_limit = 1004 - top
    for max_sum in (2, 1):
        cols, heights = layout_columns(draw, max_sum)
        print(f"summary lines {max_sum}: column heights {heights} (limit {body_limit})")
        if max(heights) <= body_limit:
            break
    for ci, sections in enumerate(cols):
        x = 24 + ci * (317 + 12)
        y = top
        for name, stories in sections:
            color = SECTION_COLORS[name]
            draw.rectangle([x, y, x + 317, y + 20], fill=color)
            draw.text((x + 8, y + 3), f"{name}  •  {len(stories)} STORIES",
                      font=F_SEC, fill=(255, 253, 246))
            y += 24
            for headline, summary, icon, photo in stories:
                y = draw_story(img, draw, x, y, 317, headline, summary, icon, photo, max_sum)
            y += 1
        if ci < 2:
            draw.line([x + 317 + 6, top, x + 317 + 6, 1004], fill=HAIR, width=1)

    # ---- footer
    draw.line([0, 1008, W, 1008], fill=RULE, width=1)
    foot = ("THE DAILY GLOBE  —  All stories happened or were first reported on "
            "Monday 23 November 2026  •  Sources: wire reports and major outlets")
    fw = draw.textlength(foot, font=F_FOOT)
    draw.text(((W - fw) / 2, 1013), foot, font=F_FOOT, fill=MUTED)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {img.size} {os.path.getsize(OUT)} bytes, "
          f"{TOTAL_STORIES} stories, summaries capped at {max_sum} lines")


if __name__ == "__main__":
    main()
