#!/usr/bin/env python3
"""news-image-20261120 — one image summing up the world news of
Friday 20 November 2026.

Pure Python 3 standard library only. No network, no files read at run
time: every pixel is drawn in code, deterministically, so two runs
write byte-identical PNGs.

Layout (1024 x 1024, newspaper front page):
  masthead  : THE WORLD IN ONE DAY / THURSDAY 19 NOVEMBER 2026
  hero      : Shenzhen summit — Trump, Xi and Putin meet three-way
  row 2     : Gulf war widens (Iran hits US bases, tankers burn) |
              Gaza — Israeli tanks cross the Yellow Line
  row 3     : Anthropic debuts at $83 a share, biggest IPO ever |
              EU lends Ukraine 45 billion euros
  footer    : The Hague — world court rules on Rohingya genocide today

All six stories were verified against Reuters / AP / CNBC / Human Rights
Watch reporting on 19 November 2026 (see NEWS.md in this repository).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
NAVY = (20, 38, 74)
NAVY_D = (12, 24, 48)
RED = (176, 42, 30)
GOLD = (201, 162, 39)
SKY = (58, 110, 165)
SKY_L = (147, 190, 224)
SEA = (28, 68, 110)
SEA_D = (16, 44, 76)
SAND = (214, 196, 150)
GREY = (90, 90, 88)
WHITE = (255, 255, 255)
GREEN = (38, 110, 66)
TEAL = (18, 96, 96)
SPACE = (8, 10, 26)
CREAM2 = (232, 224, 200)
DUSK = (250, 226, 190)
BOARD = (16, 28, 20)

# ---------------------------------------------------------------- 5x7 font
# 7 rows of 5 pixels each; "#" = on. Copy is rendered in capitals only.
FONT = {
    "A": (" .###. ", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", "..#..", ".....", ".....", ".....", "..#..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".#.#.", "..##.", ".#.#.", "####."),
}
FONT = {k: tuple(r.strip()[:5].ljust(5, ".") for r in v)
        for k, v in FONT.items()}


def _chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    return out + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


def write_png(path, rgb, w, h):
    """Deterministic PNG: filter-0 rows, zlib level 9, fixed chunk order."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for _ in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, c)

    def vline(self, x, y, h, c, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx + dy, x0, y0
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x + a, y + b, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                for xx in range(cx - rr, cx + rr + 1):
                    d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                    if rr * rr - 2 * rr <= d2 <= rr * rr:
                        self.set(xx, yy, c)

    def tri(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        for yy in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, c)

    def starburst(self, cx, cy, r0, r1, n, c):
        pts = []
        for k in range(2 * n):
            r = r1 if k % 2 == 0 else r0
            a = math.pi * k / n - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        for k in range(len(pts)):
            self.tri((pts[k], pts[(k + 1) % len(pts)], (cx, cy)), c)

    # ------------------------------------------------------------ text
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, x, y, s, scale, c):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[" "])
            for ry in range(7):
                row = g[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        self.rect(cx + rx * scale, y + ry * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        return self.draw_text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        lines, cur = [], ""
        for wd in s.upper().split():
            trial = (cur + " " + wd).strip()
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

# ---------------------------------------------------------------- palette
# (base palette PAPER/INK/NAVY/NAVY_D/RED/GOLD/SKY/SKY_L/SEA/SEA_D/SAND/
#  GREY/WHITE/GREEN/TEAL/SPACE/CREAM2/DUSK/BOARD comes from the head)
BG = (238, 230, 210)     # page background, classic pale cream (~5%)
CARD = (250, 245, 232)    # story card + header background, lighter cream
INK = (16, 24, 40)        # headline / title ink on cream
FACT_D = (70, 72, 84)     # fact text on cream
CARD_LINE = (160, 150, 125)  # warm grey card borders
DATE_RED = (168, 44, 32)  # masthead date, classic newspaper red
OCEAN = (16, 42, 76)
LAND = (94, 138, 122)     # muted sage-teal continents
GRAT = (38, 74, 112)      # graticule lines
EQUATOR = (70, 110, 150)
OCEAN_LABEL = (110, 140, 175)
MUTED = (150, 168, 192)   # secondary text on dark (map area only)
FACT_C = (214, 222, 232)  # fact text on dark (unused on cream cards)
LAND_EDGE = (150, 190, 172)  # coastline stroke
HALO = (150, 120, 30)     # marker halo

# Each story carries its own accent colour: the map marker, the number
# badge, the place kicker, the stat line and the card's top rule all use
# the same colour, so a reader can match a card to its marker at a glance.
ACCENT = {
    1: (201, 162, 39),   # gold     - Shenzhen
    2: (90, 165, 225),   # sky blue - The Hague
    3: (224, 82, 66),    # red      - Riyadh
    4: (232, 142, 44),   # orange   - Gaza
    5: (74, 178, 110),   # emerald  - Kyiv
    6: (168, 130, 220),  # violet   - New York
}

# Darker versions of the accents, for text and rules on cream: the
# bright accents are too light to read on a pale background.
ACCENT_DARK = {
    1: (150, 115, 20),   # dark gold
    2: (35, 105, 165),   # deep blue
    3: (175, 45, 35),    # brick red
    4: (185, 105, 15),   # dark amber
    5: (35, 125, 75),    # deep green
    6: (115, 80, 175),   # deep violet
}


def halo_of(color):
    return tuple(v * 11 // 20 for v in color)


def newsprint(c, x, y, w, h, line_c):
    """Ghosted newspaper background: column dividers + rows of short
    horizontal 'text' lines, drawn in a colour only just above the
    background (the 80-90% blur: barely visible, never fights the real
    copy drawn on top of it). Fully deterministic."""
    cols = 4 if w > 500 else 2
    for k in range(1, cols):
        c.vline(x + k * w // cols, y + 6, h - 12, line_c, 1)
    row = 0
    yy = y + 8
    while yy + 2 <= y + h - 6:
        for k in range(cols):
            cx0 = x + k * w // cols + 6
            cx1 = x + (k + 1) * w // cols - 6
            frac = 0.55 + 0.4 * ((row * 7 + k * 13) % 10) / 10.0
            lw = int((cx1 - cx0) * frac)
            if row == 0:
                c.hline(cx0, yy, int((cx1 - cx0) * 0.7), line_c, 4)
            elif lw > 8:
                c.hline(cx0, yy, lw, line_c, 2)
        yy += 6
        row += 1

# ------------------------------------------------------------ type tools
# The base 5x7 bitmap font only ships one weight and no tracking, so the
# display treatments below are built on top of it: bold = a second pass
# offset by 1px (thickens strokes at scale >= 2), tracking = extra px
# between glyphs. Type scale: 5 masthead date, 3 masthead title, 2 bold
# headlines/kickers/stats, 2 facts, 1 tracked labels.


def tw(s, scale, tracking=0):
    return len(s) * 6 * scale - scale + max(0, len(s) - 1) * tracking


def draw_text2(c, x, y, s, scale, color, tracking=0, bold=False):
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row[rx] == "#":
                    c.rect(cx + rx * scale, y + ry * scale, scale, scale,
                           color)
                    if bold:
                        c.rect(cx + rx * scale + 1, y + ry * scale,
                               scale, scale, color)
        cx += 6 * scale + tracking
    return cx


def text_center2(c, cx, y, s, scale, color, tracking=0, bold=False):
    return draw_text2(c, cx - tw(s, scale, tracking) // 2, y, s, scale,
                      color, tracking, bold)


def wrap2(s, scale, maxw, tracking=0):
    lines, cur = [], ""
    for wd in s.upper().split():
        trial = (cur + " " + wd).strip()
        if tw(trial, scale, tracking) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def poly_outline(c, pts, color):
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        c.line(x0, y0, x1, y1, color, 1)


def compass(c, cx, cy):
    """Small north arrow in open ocean, bottom-left of the map."""
    c.ring(cx, cy, 18, OCEAN_LABEL, 1)
    c.tri(((cx, cy - 15), (cx - 5, cy + 7), (cx + 5, cy + 7)), GOLD)
    draw_text2(c, cx - 5, cy - 32, "N", 2, WHITE)

# ------------------------------------------------------------ projection
# Equirectangular world map. Longitude -180..180 across MAP_W,
# latitude 85..-60 down MAP_H (Antarctica omitted, as usual).
MAP_X0, MAP_Y0, MAP_W, MAP_H = 24, 128, 976, 393
LAT_TOP, LAT_BOT = 85, -60


def project(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOT) * MAP_H
    return int(round(x)), int(round(y))


def fill_poly(c, pts, color):
    """Scanline polygon fill for a list of (x, y) pixel points."""
    ys = [p[1] for p in pts]
    n = len(pts)
    for y in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            if ay == by:
                continue
            if min(ay, by) <= y < max(ay, by):
                xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            x0, x1 = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
            if x1 >= x0:
                c.rect(x0, y, x1 - x0 + 1, 1, color)


# ------------------------------------------------------------ continents
# Simplified (lon, lat) outlines, hand-drawn for a 1024px map.
NORTH_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-141, 60), (-135, 57),
                 (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
                 (-110, 24), (-105, 20), (-97, 16), (-92, 15), (-86, 12),
                 (-83, 9), (-79, 9), (-83, 15), (-87, 21), (-91, 19),
                 (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 25),
                 (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 44),
                 (-64, 44), (-60, 47), (-55, 47), (-60, 52), (-64, 58),
                 (-68, 55), (-70, 60), (-78, 62), (-85, 66), (-92, 66),
                 (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71),
                 (-165, 68)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-25, 70), (-20, 74), (-22, 77), (-30, 80), (-45, 80),
             (-55, 78), (-58, 74)]
SOUTH_AMERICA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12),
                 (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
                 (-74, -50), (-70, -54), (-66, -55), (-65, -45), (-62, -41),
                 (-58, -35), (-52, -32), (-48, -28), (-41, -23), (-39, -17),
                 (-35, -9), (-35, -6), (-40, -3), (-44, -2), (-50, 0),
                 (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-77, 8)]
AFRICA = [(-17, 15), (-16, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36),
          (10, 37), (11, 34), (20, 32), (30, 31), (32, 31), (34, 28),
          (37, 22), (39, 18), (43, 12), (48, 11), (51, 12), (46, 5),
          (41, -2), (40, -10), (37, -18), (35, -25), (32, -29), (28, -33),
          (20, -35), (17, -32), (14, -22), (12, -18), (13, -12), (12, -6),
          (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12)]
EUROPE = [(-10, 36), (-9, 43), (-2, 44), (-4, 48), (0, 51), (5, 53),
          (8, 57), (5, 60), (5, 62), (12, 65), (18, 69), (25, 71),
          (30, 70), (32, 60), (32, 50), (30, 45), (28, 42), (24, 44),
          (20, 44), (16, 45), (12, 44), (8, 44), (3, 42), (0, 39),
          (-2, 37), (-6, 36)]
ASIA = [(30, 36), (27, 40), (28, 42), (33, 42), (36, 36), (35, 33),
        (39, 31), (42, 29), (44, 29), (48, 30), (50, 29), (54, 27),
        (57, 27), (60, 25), (62, 25), (66, 25), (68, 24), (71, 22),
        (73, 19), (76, 13), (77, 8), (80, 7), (80, 13), (84, 19),
        (88, 22), (91, 22), (93, 16), (94, 17), (97, 16), (98, 10),
        (100, 8), (103, 2), (104, 9), (106, 10), (109, 13), (109, 18),
        (106, 20), (108, 18), (110, 20), (114, 22), (117, 23), (120, 25),
        (121, 28), (122, 31), (120, 35), (122, 38), (124, 40), (127, 40),
        (130, 42), (132, 43), (135, 44), (137, 46), (140, 47), (142, 50),
        (142, 53), (141, 58), (142, 60), (140, 60), (145, 59), (150, 59),
        (156, 51), (158, 53), (160, 55), (162, 58), (162, 62), (170, 60),
        (178, 65), (178, 68), (172, 66), (164, 66), (158, 69), (150, 72),
        (140, 72), (130, 72), (120, 73), (112, 74), (104, 76), (100, 77),
        (95, 76), (90, 75), (85, 73), (80, 73), (75, 72), (70, 72),
        (66, 69), (60, 69), (55, 68), (50, 68), (45, 68), (40, 67),
        (35, 66), (32, 68), (30, 70), (32, 66), (35, 64), (38, 60),
        (40, 55), (42, 50), (44, 45), (42, 42), (38, 40), (35, 38),
        (32, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-3, 50)]
JAPAN = [(130, 31), (132, 33), (134, 34), (137, 35), (139, 35), (140, 38),
         (141, 41), (142, 44), (144, 44), (143, 42), (141, 39), (139, 37),
         (136, 34), (133, 33)]
INDONESIA = [(95, 5), (98, 3), (100, 0), (102, -3), (105, -6), (108, -7),
             (112, -7), (114, -8), (117, -9), (120, -10), (122, -9),
             (125, -9), (128, -8), (130, -4), (132, -2), (135, -3),
             (138, -4), (141, -3), (141, -1), (137, 1), (133, 0),
             (130, 0), (127, 1), (124, 1), (121, 0), (119, 1), (117, 3),
             (115, 4), (112, 5), (108, 3), (105, 0), (100, 2), (97, 5)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25),
              (45, -25), (43, -21)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
               (175, -40), (172, -43), (168, -46)]
ICELAND = [(-18, 63), (-14, 64), (-16, 66), (-22, 66), (-24, 64)]
SRI_LANKA = [(80, 6), (81, 8), (81, 9), (80, 9), (79, 7)]
TAIWAN = [(120, 22), (121, 24), (121, 25), (120, 25)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EUROPE,
              ASIA, AUSTRALIA, UK, JAPAN, INDONESIA, MADAGASCAR,
              NEW_ZEALAND, ICELAND, SRI_LANKA, TAIWAN]

# ------------------------------------------------------------ stories
# Six stories, each verified against at least two independent sources
# (see NEWS.md). lon/lat place the numbered marker on the map.
STORIES = [
    {"n": 1, "lon": 114.1, "lat": 22.5, "place": "SHENZHEN, CHINA",
     "headline": "TRUMP, XI, PUTIN SIGN PEACE DECLARATION",
     "fact": "UN REFORM, MORE FUEL SUPPLY, ICC WARNING, NUCLEAR TALK.",
     "stat": "4 POINTS"},
    {"n": 2, "lon": 4.3, "lat": 52.1, "place": "THE HAGUE, NETHERLANDS",
     "headline": "COURT: MYANMAR COMMITTED GENOCIDE",
     "fact": "ICJ RULES 9-6: MYANMAR GUILTY. FIRST STATE VERDICT IN 80 YEARS.",
     "stat": "9-6 VOTE"},
    {"n": 3, "lon": 46.7, "lat": 24.6, "place": "RIYADH, SAUDI ARABIA",
     "headline": "HOUTHIS HIT RIYADH TOWER",
     "fact": "MISSILES DAMAGE THE 80-STOREY PIF TOWER. NO INJURIES. OIL UP TO $92.",
     "stat": "$92 BRENT"},
    {"n": 4, "lon": 34.45, "lat": 31.5, "place": "GAZA",
     "headline": "GAZA RAID ENDS, ROAD REOPENS",
     "fact": "ISRAEL ENDS 24-HOUR RAID PAST THE LINE. HAMAS CALLS IT A BREACH.",
     "stat": "24-HOUR RAID"},
    {"n": 5, "lon": 30.5, "lat": 50.45, "place": "KYIV, UKRAINE",
     "headline": "EUROPE READY FOR UKRAINE TALKS",
     "fact": "LEADERS BACK TALKS WITH RUSSIA. UK PLEDGES 1,000 DRONES, 260M POUNDS.",
     "stat": "1,000 DRONES"},
    {"n": 6, "lon": -74.0, "lat": 40.7, "place": "NEW YORK, USA",
     "headline": "ANTHROPIC SOARS ON MARKET DEBUT",
     "fact": "FIRST AI FIRM TO GO PUBLIC. PRICED $83, CLOSED $97.17, UP 17%.",
     "stat": "+17% CLOSE"},
]


def draw_marker(c, cx, cy, n, color=GOLD):
    c.disc(cx, cy, 16, halo_of(color))
    c.disc(cx, cy, 12, color)
    c.ring(cx, cy, 14, WHITE, 2)
    s = str(n)
    draw_text2(c, cx - tw(s, 2) // 2, cy - 7, s, 2, NAVY_D, bold=True)


def story_card(c, x, y, w, h, st):
    c.rect(x, y, w, h, CARD)
    ac = ACCENT[st["n"]]
    acd = ACCENT_DARK[st["n"]]
    if st["n"] == 1:
        c.hline(x, y, w, acd, 3)
        c.hline(x, y + h - 3, w, acd, 3)
        c.vline(x, y, h, acd, 3)
        c.vline(x + w - 3, y, h, acd, 3)
    else:
        c.hline(x, y, w, acd, 3)
        c.hline(x, y + h - 1, w, CARD_LINE, 1)
        c.vline(x, y, h, CARD_LINE, 1)
        c.vline(x + w - 1, y, h, CARD_LINE, 1)
    # ghosted newspaper background behind the copy
    newsprint(c, x + 6, y + 6, w - 12, h - 12, (215, 205, 180))
    # number badge + place kicker (bold, in the story's colour)
    draw_marker(c, x + 24, y + 26, st["n"], ac)
    draw_text2(c, x + 44, y + 18, st["place"], 2, acd, bold=True)
    # headline, bold, up to 2 lines
    lines = wrap2(st["headline"], 2, w - 28)[:2]
    hy = y + 52
    for ln in lines:
        draw_text2(c, x + 14, hy, ln, 2, INK, bold=True)
        hy += 18
    # fact, up to 3 lines
    flines = wrap2(st["fact"], 2, w - 28)[:3]
    fy = hy + 6
    for ln in flines:
        draw_text2(c, x + 14, fy, ln, 2, FACT_D)
        fy += 18
    # stat highlight at the foot of the card, in the story's colour
    sy = y + h - 40
    c.hline(x + 14, sy, w - 28, CARD_LINE, 1)
    draw_text2(c, x + 14, sy + 8, st["stat"], 2, acd, bold=True)


# ------------------------------------------------------------- layout
def build():
    c = Canvas(W, H, BG)

    # ---- masthead: cream paper, ghosted newspaper, ink title, red date
    c.rect(24, 24, 976, 104, CARD)
    c.hline(24, 24, 976, INK, 3)
    c.hline(24, 125, 976, INK, 3)
    newsprint(c, 24, 24, 976, 104, (210, 198, 170))
    text_center2(c, 512, 38, "THE WORLD IN ONE DAY", 3, INK, tracking=3)
    text_center2(c, 512, 72, "FRIDAY 20 NOVEMBER 2026", 5, DATE_RED,
                 bold=True)

    # ---- map: ocean, graticule, continents with coastline stroke
    c.rect(MAP_X0, MAP_Y0, MAP_W, MAP_H, OCEAN)
    for lon in range(-180, 181, 30):
        gx, _ = project(lon, 0)
        c.vline(gx, MAP_Y0, MAP_H, GRAT, 1)
    for lat in range(-60, 86, 30):
        _, gy = project(0, lat)
        c.hline(MAP_X0, gy, MAP_W, EQUATOR if lat == 0 else GRAT, 1)
    for cont in CONTINENTS:
        pts = [project(lon, lat) for lon, lat in cont]
        fill_poly(c, pts, LAND)
        poly_outline(c, pts, LAND_EDGE)
    # ocean labels, tracked (decorative, scale 1)
    draw_text2(c, 60, 430, "PACIFIC OCEAN", 1, OCEAN_LABEL, tracking=2)
    draw_text2(c, 860, 430, "PACIFIC OCEAN", 1, OCEAN_LABEL, tracking=2)
    draw_text2(c, 380, 360, "ATLANTIC OCEAN", 1, OCEAN_LABEL, tracking=2)
    draw_text2(c, 690, 435, "INDIAN OCEAN", 1, OCEAN_LABEL, tracking=2)
    # compass rose in the open South Pacific
    compass(c, 105, 470)
    # gold frame around the map
    c.hline(MAP_X0, MAP_Y0, MAP_W, GOLD, 3)
    c.hline(MAP_X0, MAP_Y0 + MAP_H - 3, MAP_W, GOLD, 3)
    c.vline(MAP_X0, MAP_Y0, MAP_H, GOLD, 3)
    c.vline(MAP_X0 + MAP_W - 3, MAP_Y0, MAP_H, GOLD, 3)
    # numbered markers, each in its story's colour
    for st in STORIES:
        mx, my = project(st["lon"], st["lat"])
        draw_marker(c, mx, my, st["n"], ACCENT[st["n"]])

    # ---- legend line (on cream now, so ink instead of gold)
    text_center2(c, 512, 527, "NUMBERS ON THE MAP MATCH THE STORIES BELOW",
                 1, INK, tracking=2)

    # ---- story cards: 2 rows x 3 columns
    cw, ch, gap = 317, 216, 12
    for i, st in enumerate(STORIES):
        col, row = i % 3, i // 3
        x = 24 + col * (cw + gap)
        y = 540 + row * (ch + gap)
        story_card(c, x, y, cw, ch, st)

    # ---- footer
    text_center2(c, 512, 992,
                 "VERIFIED AGAINST REUTERS, BBC, AP AND OTHERS - 20 NOVEMBER 2026",
                 1, (110, 105, 90), tracking=1)
    return c


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    c = build()
    path = os.path.join(outdir, "entry.png")
    write_png(path, c.px, W, H)
    print("WROTE", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
