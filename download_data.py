#!/usr/bin/env python
"""
download_data.py — fetch the Codex per-dataset metadata (cell type / neurotransmitter /
classification tables) into data/meta/ with the exact local filenames the pipeline expects.

The five RAW EDGE-LIST CSVs (fafb_783_edge_list.csv, banc_626_edge_list.csv, ...) are the
challenge-provided files and live at the repo root — they are NOT downloaded here.

This script documents, for each metadata file:
  * the dataset and version,
  * the Codex source filename,
  * the LOCAL filename the code reads (see src/annotate.py),
and attempts to download from the documented Codex GCS path. The Codex download schema can
change; if a download fails, the script prints the precise manual mapping so you can grab the
files from the Codex "Download data" page (https://codex.flywire.ai/api/download) and rename.

Usage:  python download_data.py            # download everything missing
        python download_data.py --force    # re-download even if present
"""
import gzip
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
META = os.path.join(ROOT, "data", "meta")

# Documented Codex public GCS base. Pattern: <BASE>/<dataset>/<version>/<source_file>
# Verify against the current Codex schema if a fetch 404s.
BASE = "https://storage.googleapis.com/flywire-data/codex/data"

# (dataset, version, source_file_on_codex, local_filename, required_by_pipeline)
FILES = [
    # --- FAFB v783 (curated) ---
    ("fafb", "783", "classification.csv.gz",          "fafb_classification.csv.gz",          True),
    ("fafb", "783", "consolidated_cell_types.csv.gz", "fafb_consolidated_cell_types.csv.gz", True),
    ("fafb", "783", "neurons.csv.gz",                 "fafb_neurons.csv.gz",                 True),
    ("fafb", "783", "coordinates.csv.gz",             "fafb_coordinates.csv.gz",             False),
    ("fafb", "783", "column_assignment.csv.gz",       "fafb_column_assignment.csv.gz",       False),
    ("fafb", "783", "visual_neuron_types.csv.gz",     "fafb_visual_neuron_types.csv.gz",     False),
    # --- BANC v626 (partly predicted) ---
    ("banc", "626", "neurons.csv.gz",                 "banc_neurons.csv.gz",                 True),
    # --- MCNS v0.9 (partly predicted) ---
    ("mcns", "0.9", "neurons.csv.gz",                 "mcns_neurons.csv.gz",                 True),
]


def url_for(dataset, version, source_file):
    return f"{BASE}/{dataset}/{version}/{source_file}"


def valid_gzip(path):
    try:
        with gzip.open(path, "rb") as f:
            f.read(64)
        return True
    except Exception:
        return False


def main():
    force = "--force" in sys.argv
    os.makedirs(META, exist_ok=True)
    failures = []
    for dataset, version, src, local, required in FILES:
        dst = os.path.join(META, local)
        if not force and os.path.exists(dst) and valid_gzip(dst):
            print(f"  have   {local}")
            continue
        url = url_for(dataset, version, src)
        try:
            print(f"  GET    {url}")
            urllib.request.urlretrieve(url, dst)
            if not valid_gzip(dst):
                raise ValueError("downloaded file is not valid gzip")
            print(f"  saved  {local}")
        except Exception as e:
            failures.append((dataset, version, src, local, required, str(e)))
            if os.path.exists(dst):
                os.remove(dst)
            print(f"  FAIL   {local}: {e}")

    if failures:
        print("\n*** Some downloads failed. Get them from the Codex 'Download data' page")
        print("    (https://codex.flywire.ai/api/download) and place/rename as follows:\n")
        for dataset, version, src, local, required, _ in failures:
            tag = "REQUIRED" if required else "optional"
            print(f"    [{tag}] {dataset} v{version}: {src}  ->  data/meta/{local}")
        req_failed = any(r for *_, r, _ in failures)
        sys.exit(1 if req_failed else 0)
    print("\nAll metadata present in data/meta/.")


if __name__ == "__main__":
    main()
