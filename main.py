#!/usr/bin/env python3
"""THE WORLD DAILY - front page for Sunday, 22 November 2026.

Renders a broadsheet newspaper front page as a PNG using only the Python
standard library (struct + zlib). No network, no clock, no randomness:
the output is byte-for-byte deterministic.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1024, 984

# ---------------------------------------------------------------- palette --
PAPER = (247, 243, 232)
INK = (16, 16, 18)
GREY = (104, 102, 98)
RULE = (24, 24, 26)
RED = (156, 26, 26)
BLUE = (24, 62, 118)
GREEN = (30, 108, 66)
GOLD = (216, 166, 32)
WHITE = (248, 248, 244)

# ------------------------------------------------------------ tiny 5x7 font
# Row-major: 7 bytes per glyph, bit 4 = leftmost column.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x11, 0x0A, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F, 0x00),
    "b": (0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E, 0x00),
    "c": (0x00, 0x0F, 0x10, 0x10, 0x10, 0x0F, 0x00),
    "d": (0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F, 0x00),
    "e": (0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0F, 0x00),
    "f": (0x06, 0x09, 0x08, 0x1C, 0x08, 0x08, 0x00),
    "g": (0x00, 0x0E, 0x11, 0x11, 0x0E, 0x01, 0x06),
    "h": (0x10, 0x1E, 0x11, 0x11, 0x11, 0x11, 0x00),
    "i": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x0E, 0x00),
    "j": (0x06, 0x02, 0x02, 0x02, 0x12, 0x0C, 0x00),
    "k": (0x10, 0x12, 0x14, 0x18, 0x14, 0x12, 0x00),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E, 0x00),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x00),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x00),
    "o": (0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E, 0x00),
    "p": (0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10),
    "q": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01),
    "r": (0x00, 0x00, 0x1E, 0x10, 0x10, 0x10, 0x00),
    "s": (0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E, 0x00),
    "t": (0x08, 0x08, 0x1C, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x11, 0x11, 0x11, 0x13, 0x0D, 0x00),
    "v": (0x00, 0x11, 0x11, 0x11, 0x0A, 0x04, 0x00),
    "w": (0x00, 0x11, 0x11, 0x15, 0x15, 0x0A, 0x00),
    "x": (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00),
    "y": (0x00, 0x11, 0x11, 0x11, 0x0A, 0x04, 0x04),
    "z": (0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F, 0x00),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "'": (0x06, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x11, 0x13, 0x02, 0x04, 0x08, 0x19, 0x11),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "*": (0x00, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0x00),
    "#": (0x0A, 0x1F, 0x0A, 0x0A, 0x1F, 0x0A, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "£": (0x0C, 0x12, 0x10, 0x1E, 0x10, 0x12, 0x0D),
    "\x95": (0x00, 0x00, 0x04, 0x0E, 0x04, 0x00, 0x00),
}

# --------------------------------------------------------- pictogram art ---
# 12x12 character grids; '.' = transparent (paper shows through).
PICO_PALETTE = {
    "K": INK,
    "R": RED,
    "B": BLUE,
    "G": GREEN,
    "Y": GOLD,
    "W": WHITE,
    "g": GREY,
}

PICO = {
    # COP31: the globe, blue oceans, green land
    "globe": (
        "....BBBB....",
        "..BBBBBBBB..",
        ".BBGGGBBBBB.",
        "BGGGGGBBBBBB",
        "BGGGBBBBBBGB",
        "BBBBBBGGGGBB",
        "BGBBBBGGGGBB",
        "BGGBBBBBBBBB",
        "BGGBBBBBGGBB",
        ".BBBBBBGGBB.",
        "..BBBBBBBB..",
        "....BBBB....",
    ),
    # Iran lead: burning oil tanker on the waves
    "tanker": (
        "........RR..",
        ".......RRRR.",
        "........RR..",
        "........KK..",
        "...KK...KK..",
        "...KK...KK..",
        ".KKKKKKKKKK.",
        ".KKKKKKKKKK.",
        ".KYKKKKKKYK.",
        "..KKKKKKKK..",
        ".BB.....BBB.",
        "..BBB....BB.",
    ),
    # Poland: missile with red exhaust trail
    "missile": (
        ".........KK.",
        "........KKKK",
        ".......KKKK.",
        "......KKKK..",
        ".....KKKK...",
        "....KKKK....",
        "...KKKK.....",
        "..RRRR......",
        ".RRRR.......",
        "RRRR........",
        "RRR.........",
        "............",
    ),
    # Denmark: the Dannebrog, red with white Nordic cross
    "danmark": (
        "KKKKKKKKKKKK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KWWWWWWWWWWK",
        "KWWWWWWWWWWK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KRRRWWRRRRRK",
        "KKKKKKKKKKKK",
    ),
    # Mexico: gold law-enforcement star
    "badge": (
        ".....YY.....",
        "....YYYY....",
        "....YYYY....",
        "..YYYYYYYY..",
        "...YYYYYY...",
        "...YYYYYY...",
        "....YYYY....",
        "...YYYYYY...",
        "..YYY..YYY..",
        ".YYY....YYY.",
        "..Y......Y..",
        "............",
    ),
    # Iraq: power-station fire, red with gold core
    "flame": (
        "......R.....",
        "......RR....",
        ".....RRR....",
        ".....RRRR.R.",
        "..R.RRRRRRR.",
        ".RRRRRRRRR..",
        ".RRRYYYRRRR.",
        "RRRYYYYYRRR.",
        ".RYYYYYYRR..",
        ".RYYYYYYR...",
        "..RYYYYR....",
        "...RRRR.....",
    ),
    # Youth strike: protest placard with painted exclamation mark
    "placard": (
        "KKKKKKKKKKKK",
        "KWWWWWWWWWWK",
        "KWWWWRRWWWWK",
        "KWWWWRRWWWWK",
        "KWWWWRRWWWWK",
        "KWWWWWWWWWWK",
        "KWWWWRRWWWWK",
        "KKKKKKKKKKKK",
        ".....KK.....",
        ".....KK.....",
        ".....KK.....",
        ".....KK.....",
    ),
    # Spain: red-roofed house (housing fund)
    "house": (
        ".....KK.....",
        "....KKKK....",
        "...KKKKKK...",
        "..KKKKKKKK..",
        ".RRRRRRRRRR.",
        ".KWWWWWWWWK.",
        ".KWKKWWKKWK.",
        ".KWKKWWKKWK.",
        ".KWWWWWWWWK.",
        ".KWKKWWKKWK.",
        ".KWKKWWKKWK.",
        ".KKKKKKKKKK.",
    ),
    # Japan: snow-capped peak under falling snow
    "snow": (
        ".g...g...g..",
        "...g....g...",
        ".....KK.....",
        "....KWWK....",
        "...KWWWWK...",
        "..KWWKKWWK..",
        ".KWWKKKKWWK.",
        "KWWKKKKKKWWK",
        "KKKKKKKKKKKK",
        "..g...g...g.",
        "g....g....g.",
        "...g....g...",
    ),
    # India: six-lane Ganga bridge over blue water
    "bridge": (
        "............",
        "....K..K....",
        "....K..K....",
        "KKKKKKKKKKKK",
        "KKKKKKKKKKKK",
        ".KKK....KKK.",
        "..K......K..",
        "..K......K..",
        "..K......K..",
        "BBBBBBBBBBBB",
        ".BB..BB..BB.",
        "..BB..BB..BB",
    ),
    # Tennis: racket and ball
    "racket": (
        "..KKKKKKK...",
        "..KWWWWWK...",
        "..KWWWWWK...",
        "..KWKKKWK...",
        "..KWWWWWK...",
        "...KKKKK....",
        ".....KK.....",
        ".....KK.....",
        ".....KK.....",
        "..YYY.......",
        "..YYY.......",
        "............",
    ),
}

# --------------------------------------------------------------- stories ---
# All items are anchored to Sunday, 22 November 2026 (see design-notes.md).
BANNER_TAG = "MIDDLE EAST CRISIS - THE GULF"
BANNER_HEAD = "TRUMP DEFERS IRAN STRIKES UNTIL AFTER NEW YEAR"
BANNER_DECK = ("Three tankers are struck near the Strait of Hormuz and another "
               "off Oman; Qatar mediates in Tehran as Iran vows 'any measure' "
               "to break the US blockade")

IRAN_BODY = ("President Trump has deferred any decision on renewed strikes "
             "against Iran until after the New Year. Qatar's delegation is in "
             "Tehran to mediate; Iran demands a guarantee against renewed "
             "attacks and vows any measure to break the US blockade. Central "
             "Command denies an Iranian claim that a missile damaged an F-16.")

STORIES = {
    "cop": {
        "tag": "CLIMATE - ANTALYA",
        "head": "COP31 RUNS INTO OVERTIME WITH NO FINAL TEXT",
        "body": ("Ministers wrestle over the response to worsening global "
                 "warming as the talks blow past their deadline."),
        "pico": "globe",
    },
    "pol": {
        "tag": "WORLD - WARSAW",
        "head": "RUSSIAN MISSILES LAND ON POLISH SOIL",
        "body": ("PM calls it likely a provocation timed to NATO exercises."),
        "pico": "missile",
    },
    "den": {
        "tag": "EUROPE - COPENHAGEN",
        "head": "DENMARK EXPELS RUSSIAN DEFENCE ATTACHE",
        "body": ("Non-essential visas are halted; Ukraine backing goes on."),
        "pico": "danmark",
    },
    "mex": {
        "tag": "CRIME - MEXICO CITY",
        "head": "MOST-WANTED DRUG TRAFFICKER HELD",
        "body": ("The arrest sparks gunfights, vehicle arsons and road "
                 "blockades."),
        "pico": "badge",
    },
    "irq": {
        "tag": "DISASTER - BASRA",
        "head": "POWER STATION FIRE KILLS FOUR",
        "body": ("At least 35 are hurt in the blaze at Hartha, north of "
                 "Basra."),
        "pico": "flame",
    },
    "yth": {
        "tag": "EUROPE - 25 COUNTRIES",
        "head": "STUDENTS STRIKE OVER SCHOOLS AND CLIMATE",
        "body": ("Protests hit 73 German cities over funding, climate and "
                 "the draft."),
        "pico": "placard",
    },
    "esp": {
        "tag": "EUROPE - MADRID",
        "head": "SANCHEZ EXTENDS BANK LEVY TO FUND HOUSING",
        "body": ("The levy runs to 2027; a snap election is set for November "
                 "29."),
        "pico": "house",
    },
}

BRIEFS = [
    ("snow", "JAPAN", "Heavy snow isolates 1,000+ people in the Fukushima "
     "village of Kitashiobara; Princess Aiko returns from Singapore as ties "
     "mark 60 years."),
    ("bridge", "INDIA", "Modi opens a 9.76 km six-lane bridge over the "
     "Ganga; officials meet in Dhaka as the water treaty's December 12 "
     "expiry nears."),
    ("racket", "SPORT", "The ATP Finals champion is crowned in Turin "
     "tonight."),
]

# ------------------------------------------------------------ PNG encoder --

def write_png(path, w, h, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


# ----------------------------------------------------------------- canvas --

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.data = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.data[i:i + 3] = bytes(c)

    def fill(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w - 1, x1), min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        row = bytes(c) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.data[i:i + len(row)] = row

    def hline(self, x0, x1, y, c, thick=1):
        self.fill(x0, y, x1, y + thick - 1, c)

    def vline(self, x, y0, y1, c, thick=1):
        self.fill(x, y0, x + thick - 1, y1, c)


def grain(cv, seed=20261122):
    """Subtle deterministic paper texture."""
    s = seed
    d = cv.data
    for i in range(0, len(d), 3):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        n = ((s >> 16) & 7) - 3
        if n:
            for k in (0, 1, 2):
                v = d[i + k] + n
                if 0 <= v <= 255:
                    d[i + k] = v


def text_w(s, scale):
    return max(0, len(s) * 6 - 1) * scale


def draw_text(cv, x, y, s, scale, color, bold=0):
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for r in range(7):
            bits = g[r]
            if not bits:
                continue
            yy = y + r * scale
            for c in range(5):
                if bits & (1 << (4 - c)):
                    xx = x + c * scale
                    cv.fill(xx, yy, xx + scale - 1, yy + scale - 1, color)
        if bold:
            for r in range(7):
                bits = g[r]
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        xx = x + c * scale + bold
                        cv.fill(xx, y + r * scale, xx + scale - 1,
                                y + r * scale + scale - 1, color)
        x += 6 * scale


def wrap(s, scale, maxw):
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, maxw, lead, bold=0):
    for line in wrap(s, scale, maxw):
        draw_text(cv, x, y, line, scale, color, bold)
        y += lead
    return y


def draw_kicker(cv, x, y, tag, scale=2):
    draw_text(cv, x, y, tag, scale, RED, bold=scale // 2)
    cv.hline(x, x + text_w(tag, scale) - scale, y + 8 * scale + 1, RED, 2)
    return y + 8 * scale + 1 + 2


def draw_pico(cv, x, y, key, scale):
    art = PICO[key]
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            col = PICO_PALETTE.get(ch)
            if col:
                cv.fill(x + c * scale, y + r * scale,
                        x + c * scale + scale - 1, y + r * scale + scale - 1, col)
    return len(art) * scale, max(len(r) for r in art) * scale


# ----------------------------------------------------------------- layout --

MARGIN = 28
CONTENT = W - 2 * MARGIN  # 968


def masthead(cv):
    x0, x1 = MARGIN, W - MARGIN
    cv.hline(x0, x1, 18, RULE, 4)
    y = 26
    draw_text(cv, x0, y, "SUNDAY FINAL EDITION", 2, GREY)
    right = "WORLD EDITION - PRICE $2.50"
    draw_text(cv, x1 - text_w(right, 2), y, right, 2, GREY)

    title = "THE WORLD DAILY"
    tw = text_w(title, 7)
    draw_text(cv, (W - tw) // 2, 44, title, 7, INK, bold=2)

    cv.hline(x0, x1, 98, RULE, 3)
    cv.hline(x0, x1, 104, RULE, 1)

    y = 110
    draw_text(cv, x0, y, "VOL. CXLII - No. 32,588", 2, GREY)
    motto = "INTELLIGENCE FOR A CHANGING WORLD"
    draw_text(cv, (W - text_w(motto, 2)) // 2, y, motto, 2, GREY)
    draw_text(cv, x1 - text_w("FOUNDED 1884", 2), y, "FOUNDED 1884", 2, GREY)

    date = "Sunday, 22 November 2026"
    dw = text_w(date, 4)
    draw_text(cv, (W - dw) // 2, 128, date, 4, INK, bold=1)

    cv.hline(x0, x1, 162, RULE, 3)
    cv.hline(x0, x1, 168, RULE, 1)


def banner(cv, y):
    x = MARGIN
    ky = draw_kicker(cv, x, y, BANNER_TAG, 3)
    hy = ky + 6
    hy = draw_para(cv, x, hy, BANNER_HEAD, 6, INK, CONTENT, 48, bold=2)
    dy = hy + 8
    dy = draw_para(cv, x, dy, BANNER_DECK, 2, INK, CONTENT, 16)
    return dy


def lead_block(cv, y):
    # Left: Iran standoff body with tanker art
    lx, lw = MARGIN, 596
    art_w = 60
    draw_pico(cv, lx + lw - art_w, y, "tanker", 5)
    lby = draw_para(cv, lx, y, IRAN_BODY, 2, INK, lw - art_w - 14, 16)

    # Right: COP31 overtime
    rx, rw = 648, 348
    draw_pico(cv, rx + rw - 36, y, "globe", 3)
    ky = draw_kicker(cv, rx, y, STORIES["cop"]["tag"], 2)
    hy = ky + 8
    hy = draw_para(cv, rx, hy, STORIES["cop"]["head"], 3, INK, rw - 44, 24,
                   bold=1)
    rby = draw_para(cv, rx, hy + 6, STORIES["cop"]["body"], 2, INK, rw, 15)
    return max(lby, rby)


def grid_story(cv, x, y, story, pico_scale=2):
    draw_pico(cv, x + 309 - 12 * pico_scale, y, story["pico"], pico_scale)
    ky = draw_kicker(cv, x, y, story["tag"], 2)
    hy = ky + 6
    hy = draw_para(cv, x, hy, story["head"], 2, INK, 309 - 32, 16, bold=1)
    draw_para(cv, x, hy + 4, story["body"], 2, INK, 309, 13)


def grid(cv, y):
    keys = ["pol", "den", "mex", "irq", "yth", "esp"]
    cellw, gut = 309, 20
    pitch = 112
    for i, key in enumerate(keys):
        row, col = divmod(i, 3)
        grid_story(cv, MARGIN + col * (cellw + gut), y + row * pitch,
                   STORIES[key])
    gy1, gy2 = y, y + 2 * pitch - 6
    cv.hline(MARGIN, W - MARGIN, y + pitch - 6, GREY, 1)
    for col in (1, 2):
        gx = MARGIN + col * (cellw + gut) - gut // 2
        cv.vline(gx, gy1, gy2, GREY, 1)
    return gy2


def briefs(cv, y):
    x = MARGIN
    draw_text(cv, x, y + 4, "IN BRIEF", 2, RED, bold=1)
    yy = y + 24
    for pkey, tag, item in BRIEFS:
        draw_pico(cv, x, yy - 2, pkey, 2)
        tx = x + 32
        draw_text(cv, tx, yy, tag + ":", 2, RED, bold=1)
        tw = text_w(tag + ":", 2) + 10
        lines = wrap(item, 2, W - MARGIN - (tx + tw))
        draw_para(cv, tx + tw, yy, item, 2, INK, W - MARGIN - (tx + tw), 14)
        yy += 14 * len(lines) + 6
    return yy


def footer(cv, y):
    x0, x1 = MARGIN, W - MARGIN
    cv.hline(x0, x1, y, RULE, 3)
    cv.hline(x0, x1, y + 6, RULE, 1)
    line = ("THE WORLD DAILY - PAGE ONE - SUNDAY, 22 NOVEMBER 2026 - LATE "
            "FINAL")
    draw_text(cv, (W - text_w(line, 2)) // 2, y + 14, line, 2, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    grain(cv)
    masthead(cv)

    by = banner(cv, 178)
    cv.hline(MARGIN, W - MARGIN, by + 8, RULE, 2)
    cv.hline(MARGIN, W - MARGIN, by + 14, RULE, 1)

    ly = lead_block(cv, by + 22)
    cv.vline(636, by + 22, ly, GREY, 1)

    gy = grid(cv, ly + 22)
    byy = briefs(cv, gy + 18)
    footer(cv, byy + 14)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    write_png(path, W, H, cv.data)
    print("wrote", path)


if __name__ == "__main__":
    render()
