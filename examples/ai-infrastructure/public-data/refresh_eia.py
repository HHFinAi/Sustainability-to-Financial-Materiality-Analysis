#!/usr/bin/env python3
"""Download or re-extract the official EIA source without overwriting frozen inputs.

Python standard library only. Any changed source hash or observed value is reported;
review revisions explicitly before updating inputs.json and re-running analysis.py.
"""

import argparse
import hashlib
import json
import posixpath
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def extract(path, config):
    with zipfile.ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        sheet_id = next(s.attrib[f"{{{NS['r']}}}id"]
                        for s in workbook.findall("s:sheets/s:sheet", NS)
                        if s.attrib["name"] == config["worksheet"])
        target = next(r.attrib["Target"] for r in relationships
                      if r.attrib["Id"] == sheet_id)
        target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            tree = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(e.itertext()) for e in tree.findall("s:si", NS)]
        sheet = ET.fromstring(archive.read(target))
        selected = {}
        for row in sheet.findall("s:sheetData/s:row", NS):
            cells = {}
            for cell in row.findall("s:c", NS):
                col = "".join(c for c in cell.attrib["r"] if c.isalpha())
                value = cell.find("s:v", NS)
                if cell.attrib.get("t") == "inlineStr":
                    value = "".join(cell.find("s:is", NS).itertext())
                elif value is None:
                    continue
                elif cell.attrib.get("t") == "s":
                    value = strings[int(value.text)]
                else:
                    value = value.text
                cells[col] = value
            if cells.get("A") == "Year":
                assert cells.get("B") == "State" and cells.get("V") == "Cents/kWh", "Source columns changed"
            if cells.get("B") not in config["states"]:
                continue
            year = int(cells["A"])
            if year not in config["years"]:
                continue
            state = cells["B"]
            key = (state, year)
            if key in selected:
                raise ValueError(f"Duplicate state-year in source: {key}")
            n = row.attrib["r"]
            selected[key] = {
                "year": year, "state": state,
                "total_revenue_thousand_usd": int(cells["S"]),
                "total_sales_mwh": int(cells["T"]),
                "price_cents_per_kwh": float(cells["V"]),
                "source_id": config["source_id"],
                "locator": f"'{config['worksheet']}'!A{n}:V{n}; price V, revenue S, sales T",
            }
    expected = {(s, y) for s in config["states"] for y in config["years"]}
    if set(selected) != expected:
        raise ValueError("Source is missing a requested state-year")
    return [selected[s, y] for s in config["states"] for y in config["years"]]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--workbook", type=Path, help="Read an already downloaded source XLSX")
    source.add_argument("--download-to", type=Path, help="Download official XLSX to a new file")
    parser.add_argument("--extract-to", type=Path, help="Write a new extracted JSON for analyst comparison")
    args = parser.parse_args()
    config = json.loads((HERE / "inputs.json").read_text())["eia"]
    path = args.workbook or args.download_to
    if args.download_to:
        # Refuse to replace a file, including a repository input/output.
        with urllib.request.urlopen(config["url"], timeout=60) as response:
            payload = response.read()
        with path.open("xb") as output:
            output.write(payload)
    extracted = extract(path, config)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    summary = {"source_url": config["url"], "source_file_sha256": sha,
               "source_hash_matches_frozen": sha == config["source_file_sha256"],
               "observations_match_frozen": extracted == config["observations"],
               "row_count": len(extracted), "observations": extracted}
    if args.extract_to:
        with args.extract_to.open("x") as output:
            output.write(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "observations"}, indent=2))
    if not summary["observations_match_frozen"]:
        raise SystemExit("SOURCE_CHANGED: inspect extracted rows; no frozen input was modified")
    if not summary["source_hash_matches_frozen"]:
        raise SystemExit("SOURCE_BYTES_CHANGED: selected observations match, but inspect the new source vintage")


if __name__ == "__main__":
    main()
