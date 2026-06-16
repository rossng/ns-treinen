#!/usr/bin/env python3
"""Download NS reisplanner rolling-stock images from vt.ns-mlab.nl.

The NS reisplanner shows a little scrolling picture of the train (and its
individual carriages) that will serve a journey. Those pictures live at:

    https://vt.ns-mlab.nl/v1/images/<stem>.png

where <stem> looks like:

    <type>                          e.g. icng        (whole-train, count implied)
    <type>_<carriages>              e.g. icng_5, virm_4, slt_6
    <type>_<carriages>_<variant>    e.g. gtw_8_achterhoek

There is no public index of the available images, so this script probes a
matrix of plausible filenames and downloads every one that returns HTTP 200.
The server rate-limits bursts, so requests are throttled and retried, and the
search is staged to keep the request count sane:

  Stage 1  bare type codes + <type>_<count>     -> find which codes exist
  Stage 2  for every code that produced a hit, expand all counts + variants

Run:    python3 download.py
Output: images/<stem>.png  +  manifest.json
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = "https://vt.ns-mlab.nl/v1/images/"
ROOT = Path(__file__).parent
OUT = ROOT / "images"
MANIFEST = ROOT / "manifest.json"

UA = "ns-treinen-archiver/1.0 (+https://github.com/rossng/ns-treinen)"
MAX_WORKERS = 5

# ---------------------------------------------------------------------------
# Candidate train type codes: NS, regional (Arriva/Keolis/Qbuzz/Breng/...) and
# international operators visible on the NS reisplanner. See README.md.
# ---------------------------------------------------------------------------
TYPE_CODES = [
    # NS Intercity
    "icng", "virm", "ddz", "icm", "icr", "icrm", "ddm", "ddar",
    "koploper", "traxx", "icd",
    # NS Sprinter
    "slt", "sng", "sgm", "sgmm", "flirt", "flirt3", "protos",
    # Regional DMUs / EMUs
    "gtw", "lint", "civity", "wink", "wadloper", "buffel", "dm90", "spurt",
    "stadler", "coradia",
    # International
    "ice", "ice3", "eurostar", "thalys", "tgv", "nightjet", "railjet",
    "ecx", "ec", "berlin",
    # generic fallbacks
    "sprinter", "intercity", "ic", "spr", "trein", "unknown", "default",
]

CARRIAGE_COUNTS = list(range(1, 16))

# Regional codes that, on this server, ONLY exist with a variant suffix
# (e.g. there is no bare "gtw" or "gtw_8", only "gtw_8_achterhoek"). These
# would never enter the stage-1 hit set, so we always variant-probe them.
REGIONAL_CODES = [
    "gtw", "wink", "lint", "flirt", "protos", "civity", "spurt", "buffel",
]

# Variant suffixes (route / region / operator livery names). The only one we
# know for sure is "achterhoek" (gtw_8_achterhoek); the rest are educated
# guesses, only probed for type codes that already produced a hit.
VARIANTS = [
    "achterhoek", "vechtdal", "vechtdallijnen", "valleilijn",
    "merwedelingelijn", "kamperlijn", "maaslijn", "twente", "twents",
    "limburg", "gelderland", "drenthe", "groningen", "friesland", "fryslan",
    "noord", "zuid", "oost", "west", "wadden", "zoetermeer",
    "blauwnet", "rnet", "r-net", "breng", "arriva", "connexxion", "qbuzz",
    "keolis", "eurobahn", "abellio", "syntus", "ns", "nsinternational",
    "db", "sncf", "geel", "blauw", "rood", "wit", "groen", "zwart",
]

_print_lock = threading.Lock()


def url_for(stem: str) -> str:
    return BASE + stem + ".png"


def fetch(stem: str) -> tuple[str, int, bytes]:
    """GET a stem. Returns (stem, status, body). Retries on 429/5xx/network."""
    req = urllib.request.Request(url_for(stem), headers={"User-Agent": UA})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return stem, resp.status, resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(1.5 * (attempt + 1))
                continue
            return stem, e.code, b""
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(1.0 * (attempt + 1))
            continue
    return stem, 0, b""


def probe(stems: list[str], results: dict[str, bytes]) -> set[str]:
    """Fetch each stem; record bodies of 200s. Returns set of found stems."""
    found = set()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for stem, status, body in ex.map(fetch, stems):
            if status == 200 and body:
                found.add(stem)
                results[stem] = body
                with _print_lock:
                    print(f"  FOUND {stem}.png ({len(body)} bytes)")
    return found


def main() -> None:
    OUT.mkdir(exist_ok=True)
    results: dict[str, bytes] = {}

    # --- Stage 1: bare codes + <code>_<count> ---
    stage1 = []
    for t in TYPE_CODES:
        stage1.append(t)
        stage1.extend(f"{t}_{n}" for n in CARRIAGE_COUNTS)
    print(f"Stage 1: probing {len(stage1)} base filenames...")
    probe(stage1, results)

    # type codes that produced at least one hit
    hit_codes = sorted({s.split("_")[0] for s in results})
    print(f"\nHit type codes: {', '.join(hit_codes) or '(none)'}")

    # --- Stage 2: expand variants for codes that exist + known regional codes ---
    variant_codes = sorted(set(hit_codes) | set(REGIONAL_CODES))
    stage2 = []
    for t in variant_codes:
        for n in CARRIAGE_COUNTS:
            for v in VARIANTS:
                stage2.append(f"{t}_{n}_{v}")
                stage2.append(f"{t}_{v}")
    stage2 = sorted(set(stage2) - set(results))
    print(f"\nStage 2: probing {len(stage2)} variant filenames...")
    probe(stage2, results)

    # --- Save ---
    print(f"\nSaving {len(results)} images...")
    manifest = {}
    for stem in sorted(results):
        body = results[stem]
        (OUT / f"{stem}.png").write_bytes(body)
        manifest[stem] = {"url": url_for(stem), "bytes": len(body)}
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"Done. {len(manifest)} images in {OUT.name}/, manifest in {MANIFEST.name}")


if __name__ == "__main__":
    main()
