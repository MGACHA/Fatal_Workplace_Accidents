#!/usr/bin/env python3
"""Downloads Eurostat datasets on fatal accidents at work as TSV files.

Datasets:
  hsw_n2_02 - Fatal accidents at work by NACE Rev. 2 activity
  hsw_mi01  - Standardised incidence rate of fatal accidents at work

The databrowser links ("..._custom_xxxxx/default/table") are saved views, not
downloadable files, so this script downloads the full datasets by their codes.
Filtering (countries, years, industries) is easy to do afterwards in pandas.

Usage:  python download_files_eurostat.py              -> saves to the default folder below
        python download_files_eurostat.py other_folder -> saves to other_folder
Requires: pip install requests
"""

import gzip
import sys
import time
from pathlib import Path

import requests

DEFAULT_FOLDER = Path(r"C:\Users\micha\OneDrive\Desktop\magda\VSC\Project_15\data_eurostat")

DATASETS = {
    "hsw_n2_02": "Fatal accidents at work by NACE Rev. 2 activity",
    "hsw_mi01": "Standardised incidence rate of fatal accidents at work",
}

API = "https://ec.europa.eu/eurostat/api/dissemination"


def candidate_urls(code: str) -> list[tuple[str, bool]]:
    """Returns (url, is_gzip) pairs: bulk download first, SDMX API as fallback."""
    return [
        (f"{API}/files?file=data/{code}.tsv.gz", True),
        (f"{API}/sdmx/2.1/data/{code}?format=TSV&compressed=false", False),
    ]


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Eurostat-data-downloader/1.0)"}
RETRIES = 3


def fetch(url: str, is_gzip: bool) -> bytes:
    r = requests.get(url, headers=HEADERS, timeout=120)
    r.raise_for_status()
    data = gzip.decompress(r.content) if is_gzip else r.content

    # a valid TSV has a tab-separated header line
    first_line = data[:2000].split(b"\n", 1)[0]
    if b"\t" not in first_line:
        raise ValueError("response does not look like a TSV file")
    return data


def download(code: str, folder: Path) -> bool:
    target = folder / f"{code}.tsv"

    for url, is_gzip in candidate_urls(code):
        for attempt in range(1, RETRIES + 1):
            try:
                data = fetch(url, is_gzip)
                target.write_bytes(data)
                print(f"  OK     {target.name}  ({len(data) / 1024:.0f} KB)")
                return True
            except (requests.RequestException, OSError, ValueError) as e:
                print(f"  attempt {attempt}/{RETRIES} failed ({url}): {e}")
                time.sleep(2 * attempt)

    print(f"  ERROR  could not download {code}")
    return False


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FOLDER
    folder.mkdir(parents=True, exist_ok=True)

    print(f"Saving to: {folder.resolve()}\n")
    results = {}
    for code, description in DATASETS.items():
        print(f"{code} - {description}")
        results[code] = download(code, folder)

    ok = sum(results.values())
    print(f"\nDownloaded {ok}/{len(DATASETS)} datasets.")
    if ok < len(DATASETS):
        sys.exit(1)


if __name__ == "__main__":
    main()