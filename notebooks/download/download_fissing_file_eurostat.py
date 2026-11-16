import requests

nonfatal_path = data_dir / "hsw_n2_01.tsv"
nonfatal_url = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "hsw_n2_01?format=TSV&compressed=false"
)

if not nonfatal_path.exists():
    response = requests.get(
        nonfatal_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; Eurostat-data-analysis/1.0)"},
        timeout=120,
    )
    response.raise_for_status()
    if b"\t" not in response.content[:2000]:
        raise ValueError("Eurostat response does not look like a TSV file")
    nonfatal_path.write_bytes(response.content)
    print(f"Downloaded {nonfatal_path.name} to {data_dir}")
else:
    print(f"Using existing file: {nonfatal_path}")

nonfatal_frame = pd.read_csv(nonfatal_path, sep="\t", low_memory=False)
eurostat_data["hsw_n2_01"] = nonfatal_frame
print(f"Non-fatal accidents: {len(nonfatal_frame):,} rows, {len(nonfatal_frame.columns)} columns")