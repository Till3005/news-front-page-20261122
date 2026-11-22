#!/usr/bin/env python3
"""THE WORLD DAILY -- Sunday, 22 November 2026, front page as one PNG.

This program draws the whole page by hand into an RGB byte buffer and
pushes it through a minimal PNG encoder.  Only the Python standard
library is used (os, struct, zlib): no network, no clock, no random
source.  The paper-grain speckle is driven by a fixed-seed LCG, so two
runs emit the identical file.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

# ----------------------------------------------------------------- canvas --
PAGE_W, PAGE_H = 1024, 984
SIDE = 28                       # page margin
SPAN = PAGE_W - 2 * SIDE        # full text width across the sheet
CELL_W, GUTTER, ROW_STEP = 309, 20, 112   # wire-grid geometry
LEFT_COL = (SIDE, 596)          # twin-column lead: (x, width)
RIGHT_COL = (648, 348)

# ------------------------------------------------------------------- inks --
NEWSPRINT = (247, 243, 232)     # warm paper
TONE_TEXT = (16, 16, 18)        # near-black body ink
TONE_FAINT = (104, 102, 98)     # folio lines, hairlines
TONE_RULE = (24, 24, 26)        # heavy rules
TONE_ACCENT = (156, 26, 26)     # the one red on the page
BLUE = (24, 62, 118)
GREEN = (30, 108, 66)
GOLD = (216, 166, 32)
WHITE = (248, 248, 244)

# ------------------------------------------------------- letterforms 5x7 --
# One tuple of 7 bit-patterns per glyph, row-major; bit 4 is the leftmost
# column of the 5-wide cell.  Scaled at draw time; bold = double-strike.
GLYPHS = {
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

# ----------------------------------------------------------- spot icons ---
# 12x12 character grids.  '.' stays transparent; letters map to inks.
ICON_INKS = {
    "K": TONE_TEXT,
    "R": TONE_ACCENT,
    "B": BLUE,
    "G": GREEN,
    "Y": GOLD,
    "W": WHITE,
    "g": TONE_FAINT,
}

ICONS = {
    # Earth for the Antalya climate talks
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
    # Burning product tanker, for the Gulf lead
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
    # Missile with a red exhaust streak, for the Poland item
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
    # Dannebrog: red field, white Nordic cross
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
    # Gold marshal's star, for the Mexico arrest
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
    # Fire with a gold core, for the Basra power station
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
    # Demonstrator's placard, for the school strikes
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
    # Tiled house, for the Spanish housing levy
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
    # Snowed-in mountain, for the Fukushima village
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
    # Ganga crossing: pylons, deck, arch piers, river
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
    # Racket and ball, for the Turin final
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

# ------------------------------------------------------------ today's copy -
# Every line below is anchored to Sunday, 22 November 2026.

LEAD_KICKER = "MIDDLE EAST CRISIS - THE GULF"
LEAD_HEADLINE = "TRUMP DEFERS IRAN STRIKES UNTIL AFTER NEW YEAR"
LEAD_DECK = ("Three tankers are struck near the Strait of Hormuz and another "
             "off Oman; Qatar mediates in Tehran as Iran vows 'any measure' "
             "to break the US blockade")

IRAN_COPY = ("President Trump has deferred any decision on renewed strikes "
             "against Iran until after the New Year. Qatar's delegation is in "
             "Tehran to mediate; Iran demands a guarantee against renewed "
             "attacks and vows any measure to break the US blockade. Central "
             "Command denies an Iranian claim that a missile damaged an F-16.")

# (tag, headline, body, icon)
COP31 = ("CLIMATE - ANTALYA",
         "COP31 RUNS INTO OVERTIME WITH NO FINAL TEXT",
         "Ministers wrestle over the response to worsening global warming "
         "as the talks blow past their deadline.",
         "globe")

WIRE = (
    ("WORLD - WARSAW",
     "RUSSIAN MISSILES LAND ON POLISH SOIL",
     "PM calls it likely a provocation timed to NATO exercises.",
     "missile"),
    ("EUROPE - COPENHAGEN",
     "DENMARK EXPELS RUSSIAN DEFENCE ATTACHE",
     "Non-essential visas are halted; Ukraine backing goes on.",
     "danmark"),
    ("CRIME - MEXICO CITY",
     "MOST-WANTED DRUG TRAFFICKER HELD",
     "The arrest sparks gunfights, vehicle arsons and road blockades.",
     "badge"),
    ("DISASTER - BASRA",
     "POWER STATION FIRE KILLS FOUR",
     "At least 35 are hurt in the blaze at Hartha, north of Basra.",
     "flame"),
    ("EUROPE - 25 COUNTRIES",
     "STUDENTS STRIKE OVER SCHOOLS AND CLIMATE",
     "Protests hit 73 German cities over funding, climate and the draft.",
     "placard"),
    ("EUROPE - MADRID",
     "SANCHEZ EXTENDS BANK LEVY TO FUND HOUSING",
     "The levy runs to 2027; a snap election is set for November 29.",
     "house"),
)

# (icon, tag, one-liner)
AGATE = (
    ("snow", "JAPAN",
     "Heavy snow isolates 1,000+ people in the Fukushima village of "
     "Kitashiobara; Princess Aiko returns from Singapore as ties mark "
     "60 years."),
    ("bridge", "INDIA",
     "Modi opens a 9.76 km six-lane bridge over the Ganga; officials "
     "meet in Dhaka as the water treaty's December 12 expiry nears."),
    ("racket", "SPORT",
     "The ATP Finals champion is crowned in Turin tonight."),
)

# ------------------------------------------------------------ PNG output --

def encode_png(path, width, height, pixels):
    """Write width*height*3 RGB bytes as a minimal truecolour PNG."""
    def segment(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))

    stride = width * 3
    stream = bytearray()
    for row in range(height):
        stream.append(0)                      # filter type None per line
        stream += pixels[row * stride:(row + 1) * stride]
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n")
        fh.write(segment(b"IHDR", header))
        fh.write(segment(b"IDAT", zlib.compress(bytes(stream), 9)))
        fh.write(segment(b"IEND", b""))


# ----------------------------------------------------------------- raster --

class Page:
    """Flat RGB raster with inclusive rectangle primitives."""

    def __init__(self, width, height, tone):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(tone) * (width * height))

    def rect(self, left, top, right, bottom, tone):
        left = max(0, left)
        top = max(0, top)
        right = min(self.width - 1, right)
        bottom = min(self.height - 1, bottom)
        if right < left or bottom < top:
            return
        stripe = bytes(tone) * (right - left + 1)
        for row in range(top, bottom + 1):
            at = (row * self.width + left) * 3
            self.pixels[at:at + len(stripe)] = stripe

    def bar(self, left, right, y, tone, weight=1):
        self.rect(left, y, right, y + weight - 1, tone)

    def post(self, x, top, bottom, tone, weight=1):
        self.rect(x, top, x + weight - 1, bottom, tone)


def speckle(page, seed=20261122):
    """Press a faint fixed-seed LCG grain into the paper."""
    state = seed
    rgb = page.pixels
    for i in range(0, len(rgb), 3):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        delta = ((state >> 16) & 7) - 3
        if delta:
            for channel in (0, 1, 2):
                value = rgb[i + channel] + delta
                if 0 <= value <= 255:
                    rgb[i + channel] = value


# ------------------------------------------------------------ typesetting -

def width(s, k):
    return max(0, len(s) * 6 - 1) * k


def set_line(page, x, y, s, k, tone, weight=0):
    """Set one line; weight>0 double-strikes each pixel for a bold face."""
    for ch in s:
        pattern = GLYPHS.get(ch, GLYPHS["?"])
        for row in range(7):
            bits = pattern[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    px = x + col * k
                    py = y + row * k
                    page.rect(px, py, px + k - 1, py + k - 1, tone)
                    if weight:
                        page.rect(px + weight, py, px + weight + k - 1,
                                  py + k - 1, tone)
        x += 6 * k


def linebreak(s, k, width_limit):
    """Greedy word wrap measured against the bitmap metric."""
    lines, run = [], ""
    for word in s.split():
        candidate = word if not run else run + " " + word
        if width(candidate, k) <= width_limit:
            run = candidate
        else:
            if run:
                lines.append(run)
            run = word
    if run:
        lines.append(run)
    return lines


def set_paragraph(page, s, x, y, k, tone, width_limit, lead, weight=0):
    for line in linebreak(s, k, width_limit):
        set_line(page, x, y, line, k, tone, weight)
        y += lead
    return y


def slug(page, x, y, tag, k=2):
    """Red section kicker with its underline; returns the next baseline."""
    set_line(page, x, y, tag, k, TONE_ACCENT, weight=k // 2)
    page.bar(x, x + width(tag, k) - k, y + 8 * k + 1, TONE_ACCENT, 2)
    return y + 8 * k + 3


def stamp(page, name, x, y, k):
    """Blit a 12x12 spot icon at integer scale k."""
    art = ICONS[name]
    for row, cells in enumerate(art):
        for col, cell in enumerate(cells):
            tone = ICON_INKS.get(cell)
            if tone:
                page.rect(x + col * k, y + row * k,
                          x + col * k + k - 1, y + row * k + k - 1, tone)
    return len(art) * k, max(len(r) for r in art) * k


# --------------------------------------------------------- page furniture -

def nameplate(page):
    """Folio band, masthead title, motto row and the big date line."""
    left, right = SIDE, PAGE_W - SIDE
    page.bar(left, right, 18, TONE_RULE, 4)
    set_line(page, left, 26, "SUNDAY FINAL EDITION", 2, TONE_FAINT)
    price = "WORLD EDITION - PRICE $2.50"
    set_line(page, right - width(price, 2), 26, price, 2, TONE_FAINT)

    title = "THE WORLD DAILY"
    set_line(page, (PAGE_W - width(title, 7)) // 2, 44, title, 7,
             TONE_TEXT, weight=2)

    page.bar(left, right, 98, TONE_RULE, 3)
    page.bar(left, right, 104, TONE_RULE, 1)

    set_line(page, left, 110, "VOL. CXLII - No. 32,588", 2, TONE_FAINT)
    motto = "INTELLIGENCE FOR A CHANGING WORLD"
    set_line(page, (PAGE_W - width(motto, 2)) // 2, 110, motto, 2,
             TONE_FAINT)
    legacy = "FOUNDED 1884"
    set_line(page, right - width(legacy, 2), 110, legacy, 2, TONE_FAINT)

    dateline = "Sunday, 22 November 2026"
    set_line(page, (PAGE_W - width(dateline, 4)) // 2, 128, dateline, 4,
             TONE_TEXT, weight=1)

    page.bar(left, right, 162, TONE_RULE, 3)
    page.bar(left, right, 168, TONE_RULE, 1)


def splash(page, y):
    """Banner kicker, six-column headline and deck across the full span."""
    under_slug = slug(page, SIDE, y, LEAD_KICKER, 3)
    head_end = set_paragraph(page, LEAD_HEADLINE, SIDE, under_slug + 6, 6,
                             TONE_TEXT, SPAN, 48, weight=2)
    return set_paragraph(page, LEAD_DECK, SIDE, head_end + 8, 2,
                         TONE_TEXT, SPAN, 16)


def twincolumns(page, y):
    """Iran standoff copy left, COP31 box right; returns the deepest y."""
    lx, lw = LEFT_COL
    rx, rw = RIGHT_COL
    stamp(page, "tanker", lx + lw - 60, y, 5)
    left_end = set_paragraph(page, IRAN_COPY, lx, y, 2, TONE_TEXT,
                             lw - 60 - 14, 16)

    stamp(page, COP31[3], rx + rw - 36, y, 3)
    after_slug = slug(page, rx, y, COP31[0])
    head_end = set_paragraph(page, COP31[1], rx, after_slug + 8, 3,
                             TONE_TEXT, rw - 44, 24, weight=1)
    right_end = set_paragraph(page, COP31[2], rx, head_end + 6, 2,
                              TONE_TEXT, rw, 15)
    return max(left_end, right_end)


def wire_cell(page, x, y, tag, head, body, icon_name):
    stamp(page, icon_name, x + CELL_W - 24, y, 2)
    after_slug = slug(page, x, y, tag)
    head_end = set_paragraph(page, head, x, after_slug + 6, 2, TONE_TEXT,
                             CELL_W - 32, 16, weight=1)
    set_paragraph(page, body, x, head_end + 4, 2, TONE_TEXT, CELL_W, 13)


def wiregrid(page, y):
    """Six wire stories, three columns by two rows, with hairlines."""
    for index, (tag, head, body, icon_name) in enumerate(WIRE):
        column, row = index % 3, index // 3
        wire_cell(page, SIDE + column * (CELL_W + GUTTER), y + row * ROW_STEP,
                  tag, head, body, icon_name)
    page.bar(SIDE, PAGE_W - SIDE, y + ROW_STEP - 6, TONE_FAINT, 1)
    for column in (1, 2):
        page.post(SIDE + column * (CELL_W + GUTTER) - GUTTER // 2, y,
                  y + 2 * ROW_STEP - 6, TONE_FAINT, 1)
    return y + 2 * ROW_STEP - 6


def agaterow(page, y):
    """IN BRIEF strip: stacked one-to-two line items with spot icons."""
    set_line(page, SIDE, y + 4, "IN BRIEF", 2, TONE_ACCENT, weight=1)
    cursor = y + 24
    for icon_name, tag, item in AGATE:
        stamp(page, icon_name, SIDE, cursor - 2, 2)
        label = tag + ":"
        set_line(page, SIDE + 32, cursor, label, 2, TONE_ACCENT, weight=1)
        inset = SIDE + 32 + width(label, 2) + 10
        cursor = set_paragraph(page, item, inset, cursor, 2, TONE_TEXT,
                               PAGE_W - SIDE - inset, 14) + 6
    return cursor


def imprint(page, y):
    """Bottom rule stack and the centred edition line."""
    left, right = SIDE, PAGE_W - SIDE
    page.bar(left, right, y, TONE_RULE, 3)
    page.bar(left, right, y + 6, TONE_RULE, 1)
    line = "THE WORLD DAILY - PAGE ONE - SUNDAY, 22 NOVEMBER 2026 - LATE FINAL"
    set_line(page, (PAGE_W - width(line, 2)) // 2, y + 14, line, 2,
             TONE_FAINT)


# -------------------------------------------------------------- assembly --

def build():
    page = Page(PAGE_W, PAGE_H, NEWSPRINT)
    speckle(page)
    nameplate(page)

    deck_end = splash(page, 178)
    page.bar(SIDE, PAGE_W - SIDE, deck_end + 8, TONE_RULE, 2)
    page.bar(SIDE, PAGE_W - SIDE, deck_end + 14, TONE_RULE, 1)

    columns_end = twincolumns(page, deck_end + 22)
    page.post(636, deck_end + 22, columns_end, TONE_FAINT, 1)

    agate_top = wiregrid(page, columns_end + 22) + 18
    imprint(page, agaterow(page, agate_top) + 14)
    return page


def main():
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, "entry.png")
    page = build()
    encode_png(target, PAGE_W, PAGE_H, page.pixels)
    print("wrote", target)


if __name__ == "__main__":
    main()
