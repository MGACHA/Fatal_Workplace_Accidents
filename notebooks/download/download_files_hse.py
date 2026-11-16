#!/usr/bin/env python3
"""Downloads Excel files from the HSE statistical data tables (RIDDOR).

Source: https://www.hse.gov.uk/statistics/tables/
Usage:  python download_files_hse.py              -> saves to the default folder below
        python download_files_hse.py other_folder -> saves to other_folder
Requires: pip install requests
"""

import sys
import time
from pathlib import Path

import requests

BASE = "https://www.hse.gov.uk/statistics/assets/docs/"

DEFAULT_FOLDER = Path(r"C:\Users\micha\OneDrive\Desktop\magda\VSC\Project_15\data_hse")

# Links verified on the HSE index of data tables page
FILES = {
    "ridfatal.xlsx": "Fatal injuries 2025/26 (interim table)",
    "ridhist.xlsx": "Historical data from 1974",
    "ridagegen.xlsx": "Age, gender and industry",
    "ridkind.xlsx": "Kind of accident and industry",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; HSE-data-downloader/1.0)"}
RETRIES = 3


def download(name: str, folder: Path) -> bool:
    url = BASE + name
    target = folder / name

    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()

            # an .xlsx file is a ZIP archive - it starts with the bytes "PK"
            if not r.content.startswith(b"PK"):
                raise ValueError("downloaded file does not look like a valid .xlsx")

            target.write_bytes(r.content)
            print(f"  OK     {name}  ({len(r.content) / 1024:.0f} KB)")
            return True
        except (requests.RequestException, ValueError) as e:
            print(f"  attempt {attempt}/{RETRIES} failed for {name}: {e}")
            time.sleep(2 * attempt)

    print(f"  ERROR  {name}  ({url})")
    return False


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FOLDER
    folder.mkdir(parents=True, exist_ok=True)

    print(f"Saving to: {folder.resolve()}\n")
    results = {}
    for name, description in FILES.items():
        print(f"{name} - {description}")
        results[name] = download(name, folder)

    ok = sum(results.values())
    print(f"\nDownloaded {ok}/{len(FILES)} files.")
    if ok < len(FILES):
        sys.exit(1)


if __name__ == "__main__":
    main()