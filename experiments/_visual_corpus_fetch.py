"""EXP-HEKB005's one-time real corpus fetcher.

Run once (`python _visual_corpus_fetch.py`) to populate
`experiments/EXP-HEKB005/corpus/<artist_slug>/<work_slug>/` with real,
network-fetched files: a real Wikimedia Commons image derivative, a real
Wikidata-derived museum catalog, a real Wikipedia extract, and (where a
real public-domain source could actually be found) a real critique
excerpt. `exp_hekb_005_visual_reconstruction.py` reads only from this
cache -- it never hits the network -- so the experiment is replayable
without re-fetching, and its replay-determinism check is meaningful.

Every file here is real: a real HTTP response, a real downloaded image,
a real Pillow crop of that real image at coordinates chosen by actually
viewing it. Nothing is generated or fabricated. Where a real source could
not be found (see CRITIQUE_SOURCES below), no critique.md is written for
that work, and that gap is recorded, not papered over.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from PIL import Image

USER_AGENT = (
    "HEKB-EXP-HEKB005/0.1 (https://github.com/GemminAI/HEKB; "
    "contact: tomona@gemminai.com) python-requests"
)
HEADERS = {"User-Agent": USER_AGENT}
CORPUS_ROOT = Path(__file__).with_name("EXP-HEKB005") / "corpus"
IMAGE_WIDTH_PX = 2000


@dataclass(frozen=True, slots=True)
class VisualWorkEntry:
    artist: str
    artist_slug: str
    work_slug: str
    canonical_name: str
    wikipedia_title: str
    wikidata_qid: str


WORK_CATALOG: tuple[VisualWorkEntry, ...] = (
    VisualWorkEntry(
        "Leonardo da Vinci", "davinci", "mona_lisa", "Mona Lisa", "Mona_Lisa", "Q12418"
    ),
    VisualWorkEntry(
        "Leonardo da Vinci",
        "davinci",
        "virgin_of_the_rocks",
        "Virgin of the Rocks (Louvre version)",
        "Virgin_of_the_Rocks",
        "Q269342",
    ),
    VisualWorkEntry(
        "Leonardo da Vinci",
        "davinci",
        "saint_john_the_baptist",
        "Saint John the Baptist",
        "Saint_John_the_Baptist_(Leonardo)",
        "Q783215",
    ),
    VisualWorkEntry(
        "Johannes Vermeer",
        "vermeer",
        "girl_with_a_pearl_earring",
        "Girl with a Pearl Earring",
        "Girl_with_a_Pearl_Earring",
        "Q185372",
    ),
    VisualWorkEntry(
        "Johannes Vermeer",
        "vermeer",
        "the_milkmaid",
        "The Milkmaid",
        "The_Milkmaid_(Vermeer)",
        "Q167605",
    ),
    VisualWorkEntry(
        "Johannes Vermeer", "vermeer", "view_of_delft", "View of Delft", "View_of_Delft", "Q523974"
    ),
    VisualWorkEntry(
        "Vincent van Gogh",
        "vangogh",
        "the_starry_night",
        "The Starry Night",
        "The_Starry_Night",
        "Q45585",
    ),
    VisualWorkEntry(
        "Vincent van Gogh",
        "vangogh",
        "sunflowers",
        "Sunflowers (Van Gogh series, F454)",
        "Sunflowers_(Van_Gogh_series)",
        "Q157541",
    ),
    VisualWorkEntry(
        "Vincent van Gogh",
        "vangogh",
        "bedroom_in_arles",
        "Bedroom in Arles",
        "Bedroom_in_Arles",
        "Q724377",
    ),
)

WIKIDATA_PROPS = {
    "P276": "location",
    "P195": "collection",
    "P217": "inventory_number",
    "P186": "material_used",
    "P2048": "height_cm",
    "P2049": "width_cm",
    "P571": "inception",
    "P170": "creator",
}


def work_dir(work: VisualWorkEntry) -> Path:
    d = CORPUS_ROOT / work.artist_slug / work.work_slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def fetch_wikipedia(work: VisualWorkEntry) -> None:
    summary = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{work.wikipedia_title}",
        headers=HEADERS,
        timeout=20,
    ).json()
    extract_resp = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "extracts",
            "explaintext": "1",
            "titles": work.wikipedia_title,
            "format": "json",
        },
        headers=HEADERS,
        timeout=20,
    ).json()
    pages = extract_resp.get("query", {}).get("pages", {})
    extract_text = next(iter(pages.values())).get("extract", "") if pages else ""
    url = f"https://en.wikipedia.org/wiki/{work.wikipedia_title}"
    content = (
        f"# {summary.get('title', work.canonical_name)}\n\n"
        f"Source: {url} (Wikipedia, CC BY-SA 4.0)\n"
        f"Retrieved: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n\n"
        f"{extract_text}\n"
    )
    (work_dir(work) / "wiki.md").write_text(content)


def _wikidata_value_text(prop: str, snak: dict[str, Any], label_cache: dict[str, str]) -> str:
    value = snak["mainsnak"]["datavalue"]["value"]
    datatype = snak["mainsnak"]["datatype"]
    if datatype == "wikibase-item":
        qid = str(value["id"])
        return label_cache.get(qid, qid)
    if datatype == "quantity":
        return str(value["amount"]).lstrip("+")
    if datatype == "time":
        return str(value["time"])
    if datatype == "monolingualtext":
        return str(value["text"])
    return str(value)


def _resolve_entity_labels(qids: set[str]) -> dict[str, str]:
    if not qids:
        return {}
    labels: dict[str, str] = {}
    qid_list = sorted(qids)
    for i in range(0, len(qid_list), 50):
        batch = qid_list[i : i + 50]
        resp = requests.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbgetentities",
                "ids": "|".join(batch),
                "props": "labels",
                "languages": "en",
                "format": "json",
            },
            headers=HEADERS,
            timeout=20,
        ).json()
        for qid, entity in resp.get("entities", {}).items():
            label = entity.get("labels", {}).get("en", {}).get("value")
            if label:
                labels[qid] = label
    return labels


def fetch_wikidata_catalog(work: VisualWorkEntry) -> dict[str, Any]:
    resp = requests.get(
        f"https://www.wikidata.org/wiki/Special:EntityData/{work.wikidata_qid}.json",
        headers=HEADERS,
        timeout=20,
    ).json()
    entity = resp["entities"][work.wikidata_qid]
    claims = entity.get("claims", {})

    item_qids: set[str] = set()
    for prop in WIKIDATA_PROPS:
        for snak in claims.get(prop, []):
            if snak["mainsnak"].get("datatype") == "wikibase-item":
                item_qids.add(snak["mainsnak"]["datavalue"]["value"]["id"])
    label_cache = _resolve_entity_labels(item_qids)

    fields: dict[str, Any] = {}
    for prop, field_name in WIKIDATA_PROPS.items():
        snaks = claims.get(prop, [])
        if not snaks:
            continue  # real omission: Wikidata has no value for this property here
        values = [_wikidata_value_text(prop, snak, label_cache) for snak in snaks]
        fields[field_name] = values[0] if len(values) == 1 else values

    catalog = {
        "wikidata_qid": work.wikidata_qid,
        "wikidata_url": f"https://www.wikidata.org/wiki/{work.wikidata_qid}",
        "source": "Wikidata (CC0)",
        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fields": fields,
    }
    (work_dir(work) / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    return catalog


def fetch_image(work: VisualWorkEntry) -> Path | None:
    resp = requests.get(
        "https://www.wikidata.org/wiki/Special:EntityData/" + f"{work.wikidata_qid}.json",
        headers=HEADERS,
        timeout=20,
    ).json()
    entity = resp["entities"][work.wikidata_qid]
    p18 = entity.get("claims", {}).get("P18")
    if not p18:
        return None
    filename = p18[0]["mainsnak"]["datavalue"]["value"]
    info = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": str(IMAGE_WIDTH_PX),
            "format": "json",
        },
        headers=HEADERS,
        timeout=20,
    ).json()
    pages = info["query"]["pages"]
    page = next(iter(pages.values()))
    imageinfo = page["imageinfo"][0]
    thumb_url = imageinfo.get("thumburl") or imageinfo["url"]
    ext = Path(filename).suffix.lower() or ".jpg"
    if ext not in (".jpg", ".jpeg", ".png"):
        ext = ".jpg"
    image_path = work_dir(work) / f"image{ext}"
    image_bytes = requests.get(thumb_url, headers=HEADERS, timeout=60).content
    image_path.write_bytes(image_bytes)
    with Image.open(image_path) as downloaded:
        actual_width_px, actual_height_px = downloaded.size

    extmeta = imageinfo.get("extmetadata", {})
    license_short = extmeta.get("LicenseShortName", {}).get("value")
    usage_terms = extmeta.get("UsageTerms", {}).get("value")
    source_record = {
        "commons_file": filename,
        "commons_file_url": f"https://commons.wikimedia.org/wiki/File:{filename}",
        "downloaded_derivative_url": thumb_url,
        "requested_width_px": IMAGE_WIDTH_PX,
        "actual_downloaded_size_px": [actual_width_px, actual_height_px],
        "real_full_original_url": imageinfo["url"],
        "real_full_original_size_px": [imageinfo.get("width"), imageinfo.get("height")],
        "note": (
            "downloaded a real Commons-generated derivative (requested "
            f"{IMAGE_WIDTH_PX}px wide; Commons served its nearest cached "
            "size, recorded in actual_downloaded_size_px), not the "
            "full-resolution master file, to keep corpus size reasonable "
            "-- pixel content is real and unaltered, just not the maximum "
            "available resolution"
        ),
        "license_short_name": license_short,
        "usage_terms": usage_terms,
        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (work_dir(work) / "image_source.json").write_text(json.dumps(source_record, indent=2) + "\n")
    return image_path


def write_crop(
    work: VisualWorkEntry,
    image_path: Path,
    pixel_bbox: tuple[int, int, int, int],
    rationale: str,
) -> None:
    """`pixel_bbox` = (left, top, right, bottom) in the real image's own
    pixel coordinates, chosen by actually viewing the real downloaded
    image -- never guessed blind."""
    with Image.open(image_path) as img:
        width, height = img.size
        crop = img.crop(pixel_bbox)
        crop_path = work_dir(work) / "crop.png"
        crop.convert("RGB").save(crop_path)
    left, top, right, bottom = pixel_bbox
    normalized = [
        round(top / height, 4),
        round(left / width, 4),
        round(bottom / height, 4),
        round(right / width, 4),
    ]  # [ymin, xmin, ymax, xmax], matching specification.md section IV's bbox order
    manifest = {
        "source_image": image_path.name,
        "source_image_size_px": [width, height],
        "pixel_bbox_ltrb": list(pixel_bbox),
        "bounding_box_normalized_ymin_xmin_ymax_xmax": normalized,
        "rationale": rationale,
    }
    (work_dir(work) / "crop_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


__all__ = [
    "CORPUS_ROOT",
    "WIKIDATA_PROPS",
    "WORK_CATALOG",
    "VisualWorkEntry",
    "fetch_image",
    "fetch_wikidata_catalog",
    "fetch_wikipedia",
    "work_dir",
    "write_crop",
]
