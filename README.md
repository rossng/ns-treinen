# ns-treinen

An archive of the little scrolling train pictures that the
[NS reisplanner](https://www.ns.nl/reisplanner) shows for the rolling stock that
will serve your journey.

The images live on NS's "virtual train" image service:

```
https://vt.ns-mlab.nl/v1/images/<stem>.png
```

There is **no public index** of the available images (every listing/manifest
endpoint returns 404), so [`download.py`](./download.py) discovers them by
probing a large matrix of plausible filenames and saving every one that returns
HTTP 200. All discovered images are in [`images/`](./images), with a
[`manifest.json`](./manifest.json) recording each image's source URL and size.

## Filename scheme

| Pattern | Example | Meaning |
| --- | --- | --- |
| `<code>_<n>` | `icng_5` | NS stock; `n` = number of carriages (*bakken*) |
| `<code>_<n>_<variant>` | `gtw_8_achterhoek` | regional stock; `variant` = region/operator livery |
| `<code>` (bare) | `ice` | a few generic, count-less images |

## What's in the archive (30 images)

These are **every** filename that currently resolves — the service is not a full
fleet catalogue, just the stock NS draws in the planner.

### NS Intercity

| Image(s) | Code | Train | Routes (approx.) |
| --- | --- | --- | --- |
| `icng_5`, `icng_8` | ICNG | Intercity Nieuwe Generatie (Alstom Coradia Stream), "Wesp" | HSL-Zuid / IC Direct Amsterdam–Rotterdam–Breda, Amsterdam–Eindhoven, EuroCity Direct Amsterdam–Brussels |
| `virm_4`, `virm_6` | VIRM | Verlengd InterRegio Materieel (double-deck) | IC backbone, nationwide |
| `ddz_4`, `ddz_6` | DDZ | DubbeldekZone (double-deck EMU, ex DD-AR) | IC e.g. Den Haag–Enschede, Rotterdam–Utrecht |
| `icm_3`, `icm_4` | ICM | "Koploper" Intercity Materieel | IC toward north/east (being retired) |
| `icr`, `icr_7`, `icr_9` | ICR | Intercity Rijtuigen (loco-hauled coaches, loc 1700/TRAXX) | ex IC Brussel / IC Berlin (stock retired 2025, image lingers) |

### NS Sprinter

| Image(s) | Code | Train | Routes (approx.) |
| --- | --- | --- | --- |
| `slt_4`, `slt_6` | SLT | Sprinter Lighttrain | Randstad Sprinter services |
| `sng_3`, `sng_4` | SNG | Sprinter Nieuwe Generatie (CAF Civity) | Sprinter, nationwide |
| `sgmm_2`, `sgmm_3` | SGMm | Stadsgewestelijk Materieel ("Plan Y", modernised) | legacy Sprinter (largely retired) |
| `dm90_2` | DM90 | "Buffel" diesel multiple unit | legacy non-electrified lines (mostly sold off) |

### Regional operators (images still served by NS)

| Image(s) | Code | Train | Operator / region |
| --- | --- | --- | --- |
| `gtw_6_achterhoek`, `gtw_8_achterhoek` | GTW | Stadler GTW 2/6 & 2/8 | Arriva Achterhoek–Rivierenland |
| `gtw_6_arriva`, `gtw_8_arriva` | GTW | Stadler GTW | Arriva (generic) |
| `gtw_8_breng` | GTW | Stadler GTW 2/8 | ex-Breng/Hermes Arnhem–Doetinchem (now RRReis) |
| `gtw_6_limburg`, `gtw_8_limburg` | GTW | Stadler GTW | Arriva Limburg (Maaslijn / Heuvellandlijn) |
| `gtw_6_noord`, `gtw_8_noord` | GTW | Stadler GTW (high-res render) | Arriva Noordelijke lijnen (Groningen/Friesland) |
| `wink_2_arriva` | WINK | Stadler WINK bi-modal | Arriva Friesland |

### International

| Image | Code | Train | Route |
| --- | --- | --- | --- |
| `ice` | ICE | DB ICE 3 / ICE 3neo (Siemens Velaro) | Amsterdam–Köln–Frankfurt, Amsterdam–Berlin |
| `thalys` | — | ex-Thalys PBKA, now Eurostar (Alstom TGV family) | Amsterdam–Brussels–Paris |

## Confirmed absent

Despite being common on Dutch tracks, these returned 404 under every probed
count and operator/region suffix, so NS does not serve images for them here:
**FLIRT, LINT, Protos, Civity, SGM (un-modernised), Eurostar e320, Nightjet,
RailJet, EuroCity (ECx), TGV.** Source those elsewhere if needed.

## Usage

```bash
python3 download.py        # re-probe and refresh images/ + manifest.json
```

No dependencies beyond the Python 3 standard library. The service rate-limits
bursts, so the script throttles concurrency and retries on HTTP 429.

## Disclaimer

Images are © NS and are archived here for reference/educational purposes. All
trademarks belong to their respective operators.
