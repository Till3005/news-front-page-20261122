# THE WORLD DAILY — Sunday, 22 November 2026

A single 1024x984 PNG (`entry.png`) that sums up the day's world news,
drawn entirely by this program: a hand-written PNG encoder (`struct` +
`zlib`), a hand-built 5x7 bitmap font, and eleven hand-drawn 12x12 spot
icons. Python standard library only. No network, no clock, no RNG — the
paper grain comes from a fixed-seed LCG, so every run is byte-identical.

## Design goals

1. **Read like a broadsheet.** Thick/thin rule stacks, a full-width
   banner headline, red kickers with underlines, column hairlines and an
   agate "IN BRIEF" strip — the grammar of a real front page, at pixel
   scale.
2. **Legible when shrunk.** The judge sees the page at roughly 300 px
   wide. The banner headline is set at 6x (42 px caps), the date line at
   4x, secondary headlines at 3x, so the hierarchy survives a 3.4x
   reduction; body copy stays non-overlapping at any size.
3. **Honest determinism.** Same input, same bytes, every time.

## Layout grid (1024 x 984, 28 px margins, 968 px text span)

```
y  18-168  nameplate: folio band ("SUNDAY FINAL EDITION" / price line),
           THE WORLD DAILY at 7x bold, vol/motto/founded row,
           date line "Sunday, 22 November 2026" at 4x, rule stacks
y 178-347  splash: kicker "MIDDLE EAST CRISIS - THE GULF" at 3x,
           banner headline at 6x bold (two lines), two-line deck,
           double rule below
y 369-534  twin lead columns: Iran standoff copy (596 px + tanker icon
           at 5x) | COP31 overtime box (348 px + globe at 3x),
           hairline gutter at x 636
y 556-774  wire grid: 6 stories, 3 columns x 2 rows (cells 309 px,
           20 px gutters, 112 px row pitch), icons at 2x, hairline
           between rows, column posts
y 792-916  IN BRIEF: three agate items (Japan snow, India bridge, ATP)
y 930-958  imprint: rule stack + centred "PAGE ONE ... LATE FINAL" line
```

Every section starts from the measured bottom of the previous one
(`set_paragraph` returns the next baseline), so nothing is hard-coded to
overlap.

## Typographic system

- One 5x7 pixel font, uppercase and lowercase with true descenders,
  digits and punctuation, scaled x2–x7. Bold is a double-strike shifted
  1–2 px; lowercase bodies sit in rows 1–5 so g/j/p/q/y descend cleanly.
- Measure is exact: `width = (6*len - 1) * scale`; wrapping is a greedy
  word wrap against that metric, so a line never overruns its column.
- Colour discipline: warm newsprint, one near-black ink, grey for
  furniture, and a single accent red reserved for kickers, the IN BRIEF
  label and blood/fire in the icons.

## Spot icons

Twelve-by-twelve character grids stamped at integer scales: burning
tanker (lead), globe (COP31), missile (Poland), Dannebrog (Denmark),
marshal's star (Mexico), fire (Basra), placard (school strikes), house
(Spain), snowbound peak (Japan), Ganga bridge (India), racket (ATP).

## The day's coverage (all Sunday, 22 November 2026)

- **Lead** — Trump defers any decision on renewed Iran strikes until
  after the New Year; three tankers struck near the Strait of Hormuz
  and another off Oman; Qatar mediates in Tehran; Iran vows "any
  measure" to break the US blockade and demands a guarantee against
  renewed attacks; Central Command denies a missile damaged an F-16.
- **Antalya** — COP31 runs into overtime, no final text.
- **Grid** — Russian missiles and a suspected drone on Polish soil (PM
  calls it a provocation timed to NATO exercises); Denmark expels
  Russia's defence attache and halts non-essential visas ("enough is
  enough"); one of the FBI's most-wanted drug traffickers held in
  Mexico, with gunfights and blockades; Hartha power-station fire north
  of Basra kills four, injures 35; "international youth strike" in 25+
  countries (73 German cities); Sanchez extends the banking levy to
  2027 for housing, snap election on November 29.
- **In brief** — 1,000+ isolated by snow in Kitashiobara, Fukushima,
  and Princess Aiko back from Singapore (60 years of ties); Modi opens
  a 9.76 km six-lane Ganga bridge with the water treaty expiring
  December 12; ATP Finals champion crowned in Turin tonight.

## Determinism guarantees

- No `random`, `time`, or `datetime` imports; the speckle LCG uses the
  classic glibc constants (`state*1103515245 + 12345`, masked to 31
  bits) seeded with 20261122.
- One IDAT chunk, `zlib.compress(..., 9)`, filter byte 0 on every
  scanline, fixed IHDR fields — the encoder has no degree of freedom.
- The only file written is `<MAKEFUN_OUTPUT_DIR>/entry.png`.

## Verification

`MAKEFUN_OUTPUT_DIR=.kit/new_out python3 main.py` then
`shasum .kit/new_out/entry.png` — matches the checked-in reference
`.kit/orig_out/entry.png`, sha `143c9a379eca2fc7d20168304804c8aeffd463f4`
(1024x984, 486,555 bytes: valid PNG, under 1 MiB, longest side 1024 px).
