# THE WORLD DAILY — front page for Saturday, 21 November 2026

One 1600x1000 PNG (`entry.png`) summarising the day's news, rendered with the
Python standard library only (`struct` + `zlib`): a hand-written PNG encoder,
a hand-authored 5x7 bitmap font, and 10 hand-drawn pixel-art pictograms.
Fully deterministic (fixed LCG seed for the paper grain), no network, no
clock, no files written outside `MAKEFUN_OUTPUT_DIR`.

## Masthead

**THE WORLD DAILY** — Vol. CXLII, No. 32,587 — "Saturday, 21 November 2026"
set large and centred, flanked by folio lines, motto and thick/thin rules.
The footer repeats the date ("every item as reported on Saturday,
21 November 2026") so the day is named twice on the page.

## The day's stories (all anchored to 21 November 2026)

Lead pair (top, large):

1. **COP31 overtime in Antalya** — CLIMATE / world.
   The UN climate summit COP31 was awarded at COP30 (Belem, Nov 2025) to
   Antalya, Turkey, for November 2026; closing plenaries run into the final
   weekend. Headline dates the plenary to Saturday, 21 November 2026.

2. **GTA VI launch weekend** — GAMES / culture-tech lead.
   Rockstar's Grand Theft Auto VI is released Thursday, 19 November 2026
   (date announced by Rockstar in May 2025); its first-weekend sales records
   are the news of Saturday, 21 November.

Grid (six stories, three columns x two rows):

3. **Las Vegas Grand Prix tonight** — SPORT.
   The 2026 F1 calendar (published June 2025) puts the Las Vegas GP on
   Saturday, 21 November 2026 — a night race in F1's new-for-2026 engine
   era, with Cadillac's debut season on the street circuit.

4. **Kyiv, fifth wartime winter** — WAR IN UKRAINE / world.
   Full-scale invasion began 24 February 2022; the winter of 2026-27 is the
   fifth. Grid strikes and rolling blackouts reported on Friday 20 November
   carry into Saturday's paper; talks stalled.

5. **ATP Finals semis in Turin** — TENNIS / sport.
   The 2026 Nitto ATP Finals in Turin run 15-22 November 2026; the
   semifinals are played Saturday, 21 November, final on Sunday. (Turin
   hosts through 2030.)

6. **APEC closes in Shenzhen** — TRADE / world-economy.
   China hosts APEC 2026 in Shenzhen (announced November 2024); leaders'
   week lands in mid-November 2026 and the communique lands with Saturday's
   papers. Third time China has hosted (2001, 2014, 2026).

7. **House control undecided after midterms** — US POLITICS.
   The US midterm elections were held Tuesday, 3 November 2026; three weeks
   later recounts and litigation over a handful of districts are still
   first-page news as Congress returns.

8. **Global Carbon Budget 2026** — SCIENCE.
   The annual Global Carbon Budget report is published each November during
   the COP week; the 2026 edition lands during the Antalya summit and
   reports another record year for fossil CO2.

In-brief strip (bottom, one line each):

9. **Record Thanksgiving rush** — TRAVEL / US.
   Thanksgiving falls on Thursday, 26 November 2026; TSA record-travel
   projections are released the Friday/Saturday before (Nov 20-21, 2026).

10. **GTA VI tops The Game Awards nominations** — CULTURE.
    TGA nominations are unveiled in mid-November each year (Dec ceremony);
    in 2026 they land in the same week as the game's 19 November release.

## Page map (1600 x 1000)

```
y  40-230   masthead: folio line / title / thick-thin rules / motto /
            large date line "Saturday, 21 November 2026"
y 236-430   lead pair: COP31 (left) + GTA VI (right), pictograms x7,
            centre divider rule
y 470-492   double rule
y 492-840   3 x 2 story grid with pictograms x3, column hairlines
y 852-926   IN BRIEF: Thanksgiving travel + Game Awards (pictograms x2)
y 936-985   footer rule + repeating the day's date
```

## Design notes

- Broadsheet conventions: thick/thin rule stack, red kicker + underline per
  story, column hairlines, "IN BRIEF" strip, folio line, price line.
- Palette: warm paper (247,243,232), near-black ink, single accent red,
  small doses of blue/green/gold/orange in pictograms only.
- Type is a custom 5x7 pixel font (uppercase, lowercase with true
  descenders, digits, punctuation), scaled x2-x10 and double-struck for
  bold headlines. Lowercase bodies sit rows 1-5 so g/j/p/q/y descend into
  row 6.
- Pictograms are 12x12 character grids scaled x3 (grid) and x7 (leads):
  globe, gamepad, F1 car, flag, racket, container ship, ballot box,
  emissions chart, airliner, trophy.
- Verification: two consecutive runs produce identical SHA-256; the PNG is
  parsed back (IHDR/IDAT/IEND, CRC-checked) as a valid complete 1600x1000
  image.
