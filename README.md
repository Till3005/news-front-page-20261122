# The World Daily — 22 November 2026

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Till3005/news-front-page-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard)
[![reward](https://make.fun/badge/news-image-20261122/Till3005/news-front-page-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122)

A broadsheet front page summing up Sunday 22 November 2026's world news —
banner lead on the Gulf standoff, six wire stories in a grid, an agate
briefs strip — rendered to a 1024x984 PNG with nothing but the Python
standard library (hand-rolled PNG encoder, hand-drawn bitmap font and
spot icons). Fully deterministic: no network, no clock, no randomness.

Run: `MAKEFUN_OUTPUT_DIR=out python3 main.py` writes `out/entry.png`.

See [design-notes.md](design-notes.md) for the layout grid, type system
and determinism guarantees.
