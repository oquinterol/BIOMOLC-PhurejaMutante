#!/usr/bin/env python3
"""Produce descriptive count/CPM tables; deliberately no DE tests or p-values."""
import argparse
import csv
import json
import math
from pathlib import Path
import yaml
from pipeline_common import load_samples


def read_counts(path):
    with open(path) as f:
        reader = csv.reader((l for l in f if not l.startswith("#")), delimiter="\t")
        header = next(reader)
        if header[:6] != ["Geneid", "Chr", "Start", "End", "Strand", "Length"] or len(header) != 7:
            raise ValueError("Expected featureCounts output for exactly one sample")
        counts, lengths = {}, {}
        for row in reader:
            if len(row) != 7 or row[0] in counts:
                raise ValueError("Malformed/duplicate featureCounts row")
            gene = row[0]
            count, length = int(row[6]), int(row[5])
            if count < 0 or length <= 0:
                raise ValueError("Counts must be non-negative; exon length must be positive")
            counts[gene], lengths[gene] = count, length
    return counts, lengths


def write_table(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(header)
        w.writerows(rows)


def summarize(config, countdir, outdir):
    samples = load_samples(config)
    ids = list(samples)
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    matrix, gene_lengths, statuses = {}, None, {}
    for sid in ids:
        path = Path(countdir) / f"{sid}.tsv"
        counts, lengths = read_counts(path)
        if gene_lengths is not None and lengths != gene_lengths:
            raise ValueError("Gene IDs/exonic lengths differ across samples")
        gene_lengths = lengths
        matrix[sid] = counts
        with open(str(path) + ".summary") as f:
            rows = list(csv.reader(f, delimiter="\t"))
        statuses[sid] = {r[0]: int(r[1]) for r in rows[1:]}
        if statuses[sid].get("Assigned") != sum(counts.values()):
            raise ValueError(f"Assigned count does not equal matrix total for {sid}")
    genes = sorted(gene_lengths)
    totals = {sid: sum(matrix[sid].values()) for sid in ids}
    # An all-zero assigned library is not a valid abundance normalization baseline.
    cpm = {sid: {g: matrix[sid][g] * 1e6 / totals[sid] if totals[sid] else None
                 for g in genes} for sid in ids}
    pseudo = float(config["analysis"].get("pseudocount_cpm", 1))
    write_table(out / "raw_counts.tsv", ["gene_id", *ids],
                ([g, *(matrix[s][g] for s in ids)] for g in genes))
    write_table(out / "cpm.tsv", ["gene_id", *ids],
                ([g, *(cpm[s][g] if cpm[s][g] is not None else "NA" for s in ids)] for g in genes))
    write_table(out / "log2_cpm.tsv", ["gene_id", *ids],
                ([g, *(math.log2(cpm[s][g] + pseudo) if cpm[s][g] is not None else "NA" for s in ids)] for g in genes))
    write_table(out / "gene_lengths.tsv", ["gene_id", "union_exonic_length_bp"],
                ([g, gene_lengths[g]] for g in genes))
    write_table(out / "library_sizes.tsv", ["sample_id", "assigned_exonic_units", "zero_library"],
                ([s, totals[s], totals[s] == 0] for s in ids))
    write_table(out / "samples.tsv", ["sample_id", "genotype", "stage", "layout", "strandedness"],
                ([s, *(samples[s][k] for k in ["genotype", "stage", "layout", "strandedness"])] for s in ids))
    rows = []
    cutoff = int(config["analysis"].get("low_count_threshold", 10))
    for contrast in config["analysis"].get("contrasts", []):
        n, d = contrast["numerator"], contrast["denominator"]
        for g in genes:
            ratio = math.log2((cpm[n][g] + pseudo) / (cpm[d][g] + pseudo)) if totals[n] and totals[d] else "NA"
            rows.append([contrast["name"], g, n, d, ratio,
                         max(matrix[n][g], matrix[d][g]) < cutoff])
    write_table(out / "descriptive_ratios.tsv",
                ["contrast", "gene_id", "numerator", "denominator", "log2_cpm_ratio", "low_counts_both"], rows)
    report = {"analysis_mode": "exploratory", "smoke": config.get("smoke", {}).get("enabled", False),
              "reference_name": config["reference"]["name"], "genes": len(genes), "samples": len(ids),
              "assigned_exonic_units": totals, "featurecounts_status": statuses,
              "cpm_denominator": "sum of assigned exonic counts per sample, not all sequenced reads",
              "pseudocount_cpm": pseudo, "low_count_threshold": cutoff,
              "zero_libraries": [s for s in ids if totals[s] == 0],
              "library_assumptions": [s for s in ids if samples[s]["strandedness"] == "unknown"],
              "limitations": ["No biological replicates; no p-values, FDR or significance claims",
                              "CPM is compositional and does not measure absolute expression",
                              "Gene differences can reflect genotype/reference mapping bias",
                              "Smoke subsets are technical tests, not biological estimates",
                              "Single-end counts are reads; paired-end counts are fragments"]}
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--countdir", required=True)
    p.add_argument("--outdir", required=True)
    a = p.parse_args()
    with open(a.config) as f:
        cfg = yaml.safe_load(f)
    print(json.dumps(summarize(cfg, a.countdir, a.outdir), indent=2))
