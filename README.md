[![news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/at79x/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/at79x/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# news-image-20261120 — The World in One Day

A program that draws one image summing up the world news of **Friday 20
November 2026**, as an entry for the [make.fun bounty "Sum up 20
November's world news in one image"](https://make.fun/bounty/news-image-20261120).

`main.py` (Python 3, standard library only, no network) draws the image
from scratch and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png`. Two runs
produce byte-identical output.

A new look for this edition, after the newspaper front pages of 18 and 19
November: classic cream paper (with a ghosted newspaper-column texture)
around a dark world map with numbered gold markers. Each of the six stories
has its own accent colour — gold, sky blue, red, orange, emerald, violet —
used for its map marker and matched in its story card, so a card can be
matched to its marker at a glance.

## The six stories (all verified against Reuters / BBC / AP and others, 20 Nov 2026)

1. **Shenzhen — the peace declaration.** Trump, Xi and Putin sign a
   four-point "Declaration toward Peace": UN reform, more fuel supply, ICC
   warning, nuclear talk.
2. **The Hague — genocide verdict.** The ICJ rules 9-6 that Myanmar
   committed genocide against the Rohingya — the first state verdict in 80
   years.
3. **Riyadh — tower hit.** Houthi missiles damage the 80-storey PIF Tower.
   No injuries. Oil up to $92.
4. **Gaza — raid ends.** Israel ends a 24-hour raid past the Yellow Line;
   the Salah al-Din road reopens.
5. **Kyiv — talks ready.** European leaders back talks with Russia. The UK
   pledges 1,000 drones and 260M pounds.
6. **New York — Anthropic debuts.** The first AI firm to go public: priced
   $83, closed $97.17, up 17%.

See [NEWS.md](NEWS.md) for the sources behind each story.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Output: `out/entry.png` — 1024x1024 PNG, about 31 KB.
