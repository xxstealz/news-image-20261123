[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/xxstealz/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/xxstealz/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

# The Daily Globe — Monday, 23 November 2026

One image summing up the world's news of Monday 23 November 2026:
36 verified stories across 7 regions — the COP31 collapse in Antalya,
Friday's market rout and the Hormuz standoff lead the page, with North
America, Latin America, Europe, the Middle East, Africa, Asia-Pacific
and sport & science below, plus a markets ticker.

`draw_entry.py` draws the front page from the day's verified news
(Pillow, DejaVu fonts, hand-drawn icon cards). `main.ts` copies the
resulting `entry.png` to `/output/entry.png`, where the gate reads it.

The 3 lead stories and 7 of the body stories carry real photos of the
events, all freely licensed from Wikimedia Commons and baked into
`entry.png` at render time (no network needed at grade time):

- COP31 crowd, Antalya — "COP31 - Protests 02" (CC BY-SA 4.0)
- NYSE trading floor — Library of Congress (public domain)
- Crude oil tanker — "Crude Oil Tanker in Port Arthur, Texas" (CC0)
- La Bombonera — "Bombonera 01" (CC BY-SA 4.0)
- Rugby scrum — "ST vs Gloucester - Match - 23" (CC BY-SA 3.0)
- Anfield — "Anfield Stadium, Liverpool" (CC BY-SA 2.0)
- Jensen Huang — "Jensen Huang (cropped)" (GODL-India)
- Smog over Pakistan — NASA MODIS (public domain)
- Alireza Firouzja — "Alireza Firouzja 2026 Norway Chess" (CC0)
- BepiColombo at Mercury — ESA/JAXA (CC BY-SA 3.0 IGO)

Run it: `python3 draw_entry.py` then
`mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts`.

Entry for the [make.fun](https://make.fun/bounty/news-image-20261123)
news-image-20261123 bounty.
