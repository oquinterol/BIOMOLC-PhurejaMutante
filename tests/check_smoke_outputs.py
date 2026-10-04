#!/usr/bin/env python3
"""Check technical smoke artifacts; never interpret them as biological evidence."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def table(path):
    with path.open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def check(root):
    root = Path(root)
    ref = json.loads((root / "reference/manifest.json").read_text())
    report = json.loads((root / "tables/report.json").read_text())
    runtime = json.loads((root / "provenance/runtime.json").read_text())
    require(ref["smoke_reference"] and report["smoke"], "Not a technical smoke run")
    require(report["analysis_mode"] == "exploratory", "Unexpected analysis mode")
    require(ref["gene_count"] == report["genes"] > 0, "Reference/count gene mismatch")
    counts = table(root / "tables/raw_counts.tsv")
    cpm = table(root / "tables/cpm.tsv")
    require(len(counts) == len(cpm) == report["genes"], "Matrix row counts differ")
    require([r["gene_id"] for r in counts] == [r["gene_id"] for r in cpm], "Matrix gene IDs differ")
    for sid, total in report["assigned_exonic_units"].items():
        require(total > 0, f"No assigned reads/fragments for {sid}; adjust the smoke region/input")
        require(sum(int(r[sid]) for r in counts) == total, f"Count total mismatch: {sid}")
        require(abs(sum(float(r[sid]) for r in cpm) - 1e6) < 1e-5, f"CPM total mismatch: {sid}")
        for mate in (["R1", "R2"] if runtime["samples"][sid]["layout"] == "paired" else ["R1"]):
            fixture = root / f"reads/{sid}_{mate}.fastq.gz"
            meta = json.loads((root / f"logs/subset/{sid}_{mate}.json").read_text())
            require(hashlib.sha256(fixture.read_bytes()).hexdigest() == meta["subset_sha256"], "Subset hash mismatch")
            records = 0
            with gzip.open(fixture, "rb") as f:
                while header := f.readline():
                    seq, plus, qual = [f.readline().rstrip(b"\r\n") for _ in range(3)]
                    require(header.startswith(b"@") and plus.startswith(b"+") and seq and len(seq) == len(qual), "Invalid fixture FASTQ")
                    records += 1
            require(records == meta["reads"], "Subset record count mismatch")
        for original in runtime["samples"][sid]["files"].values():
            stat = Path(original["path"]).stat()
            require((stat.st_size, stat.st_mtime_ns) == (original["bytes"], original["mtime_ns"]), "Source changed since validation")
    require((root / "qc/multiqc_report.html").stat().st_size > 0, "Missing MultiQC report")
    require((root / "qc/multiqc_report_data").is_dir(), "Missing MultiQC data")
    print(f"Smoke OK: {report['samples']} samples, {report['genes']} genes; count/CPM totals and subset hashes consistent.")
    print("This validates processing, not biological differences or complete source-file integrity.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir", default="result/snakemake-smoke")
    check(p.parse_args().output_dir)
