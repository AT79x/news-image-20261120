# Build notes — news-image-20261120

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024 PNG, ~23 KB).

## Determinism check

```sh
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python3 main.py
MAKEFUN_OUTPUT_DIR=out2 python3 main.py
sha256sum out1/entry.png out2/entry.png   # must be identical
```

Verified 20 Nov 2026: both runs
`c410e86d8588e69c99d361827124f8bcafe2b4a279b8b22918e663ffb42958d9`
(31,179 bytes, 1024x1024, valid PNG).

## Design

- Pure Python 3 standard library only (`math`, `os`, `struct`, `zlib`).
  No network, no files read at run time, no randomness, no clock.
- Hand-written 5x7 bitmap font (same font as the 18 and 19 Nov entries),
  all copy in capitals.
- NEW LOOK for this edition: a dark world map instead of the newspaper
  front page. Equirectangular projection, hand-drawn continent outlines,
  graticule every 30 degrees, numbered gold markers at each story's
  location; six story cards below the map, numbers matching the markers.
- Typography and graphics revision (20 Nov, per AT's review — content
  unchanged): the bitmap font ships one weight and no tracking, so display
  treatments are built on top of it — bold = a second pass offset 1px,
  tracking = extra px between glyphs. Type scale: 5 masthead date (bold),
  3 tracked masthead title, 2 bold headlines/kickers/stats, 2 facts,
  1 tracked labels. Coastline stroke on every continent, halo + white
  ring on markers, compass rose in the open South Pacific, tracked ocean
  labels, a gold stat highlight at the foot of each card (number taken
  from its own fact line), full gold frame on the hero card.
- Colour revision (20 Nov, per AT's review — content unchanged): each
  story has its own accent colour — 1 gold, 2 sky blue, 3 red, 4 orange,
  5 emerald, 6 violet — used for the map marker, the card's number badge,
  place kicker, stat line and top rule, so a card matches its marker.
- Newspaper background (20 Nov, per AT's review): the masthead band and
  every story card carry a ghosted newspaper texture — column dividers
  plus rows of short 'text' lines with a headline bar per column — drawn
  in a colour only just above the background (the 80-90% blur: barely
  visible, never fights the copy on top of it). The map area is untouched.
- Cream paper revision (20 Nov, per AT's review — the navy texture was
  invisible against the ocean colour): everything outside the map is now
  classic pale cream (~5% tint) — page, masthead band and story cards —
  while the map stays dark navy. Copy on cream flipped to ink: navy
  headlines, dark-grey facts, darker variants of the six story accents
  for kickers/stats/rules (bright accents stay for the marker/badge
  discs). Masthead title in ink, date in classic newspaper red, rules in
  ink. The newspaper texture is now drawn slightly darker than the cream,
  so the columns read clearly without hurting readability.
- Six stories, each verified against at least two independent sources —
  see NEWS.md for sources.
- `out1/` and `out2/` are local test outputs only; do not commit them.
  The repository ships no pre-rendered `entry.png`: `main.py` draws the
  image fresh on every run.
- `main-base.py` is the 19 Nov generator the font/canvas/PNG writer were
  copied from; `middle.py` is the new map design section spliced into
  `main.py`. Keep both for reference; `main.py` is the deliverable.
