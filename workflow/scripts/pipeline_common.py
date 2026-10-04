"""Configuration/sample validation for exploratory RNA-seq workflows."""
import csv
import math
from pathlib import Path
import re


def load_samples(config):
    if config.get("analysis", {}).get("mode") != "exploratory":
        raise ValueError("Only exploratory analysis is implemented; no unreplicated DE tests")
    smoke = config.get("smoke", {}).get("enabled", False)
    if not isinstance(smoke, bool):
        raise ValueError("smoke.enabled must be boolean")
    allow_unknown = config.get("allow_unconfirmed_library", False)
    if not isinstance(allow_unknown, bool):
        raise ValueError("allow_unconfirmed_library must be boolean")
    if allow_unknown and not smoke:
        raise ValueError("Unconfirmed libraries are allowed only for technical smoke tests")
    pseudo = float(config.get("analysis", {}).get("pseudocount_cpm", 1))
    if not math.isfinite(pseudo) or pseudo <= 0:
        raise ValueError("pseudocount_cpm must be finite and positive")
    cutoff = config.get("analysis", {}).get("low_count_threshold", 10)
    if not isinstance(cutoff, int) or isinstance(cutoff, bool) or cutoff < 0:
        raise ValueError("low_count_threshold must be a non-negative integer")
    root = Path(config.get("data_root", ".")).resolve()
    samples = {}
    with Path(config["samples"]).open(newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        required = {"sample_id", "fastq1", "fastq2", "layout", "strandedness", "stage", "genotype"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Sample table requires columns: {sorted(required)}")
        for row in reader:
            sid = row["sample_id"]
            if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", sid):
                raise ValueError(f"Unsafe or empty sample ID: {sid!r}")
            if sid in samples:
                raise ValueError(f"Duplicate sample ID: {sid}")
            if row["layout"] not in {"single", "paired"}:
                raise ValueError(f"Invalid layout for {sid}")
            if row["strandedness"] not in {"unstranded", "forward", "reverse", "unknown"}:
                raise ValueError(f"Invalid strandedness for {sid}")
            if row["strandedness"] == "unknown" and not allow_unknown:
                raise ValueError(f"Confirm strandedness for {sid}; unknown is only allowed in smoke tests")
            if not row["stage"] or not row["genotype"]:
                raise ValueError(f"Missing stage/genotype for {sid}")
            for key in ["fastq1", "fastq2"]:
                if row[key]:
                    path = (root / row[key]).resolve()
                    if not path.is_file():
                        raise ValueError(f"Missing {key} for {sid}: {path}")
                    row[key] = str(path)
            if not row["fastq1"]:
                raise ValueError(f"Missing fastq1 for {sid}")
            if (row["layout"] == "paired") != bool(row["fastq2"]):
                raise ValueError(f"Layout/read-pair mismatch for {sid}")
            if row["fastq1"] == row["fastq2"]:
                raise ValueError(f"Identical mates for {sid}")
            row["count_strand"] = {"unstranded": 0, "unknown": 0, "forward": 1, "reverse": 2}[row["strandedness"]]
            samples[sid] = row
    if not samples:
        raise ValueError("Empty sample table")
    for c in config.get("analysis", {}).get("contrasts", []):
        if c["numerator"] not in samples or c["denominator"] not in samples:
            raise ValueError("Contrast refers to an unknown sample")
        if c["numerator"] == c["denominator"]:
            raise ValueError("A contrast must compare distinct samples")
        if samples[c["numerator"]]["stage"] != samples[c["denominator"]]["stage"]:
            raise ValueError("Descriptive mutant/control ratios must use the same stage")
    return samples
