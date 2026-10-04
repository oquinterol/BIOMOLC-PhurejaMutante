#!/usr/bin/env python3
"""Record runtime/configuration and validate read prefixes without altering sources."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import subprocess
import sys
import yaml
from pipeline_common import load_samples


def prefix_names(path, limit=100):
    opener = gzip.open if str(path).endswith(".gz") else open
    names = []
    with opener(path, "rt") as f:
        for _ in range(limit):
            h = f.readline().strip()
            if not h:
                break
            seq, plus, qual = [f.readline().rstrip("\r\n") for _ in range(3)]
            if (not h.startswith("@") or not plus.startswith("+") or not seq
                    or len(seq) != len(qual) or any(not 33 <= ord(c) <= 126 for c in qual)):
                raise ValueError(f"Malformed four-line FASTQ prefix: {path}")
            name = h.split()[0]
            if name.endswith(("/1", "/2")):
                name = name[:-2]
            names.append(name)
    if not names:
        raise ValueError(f"Empty FASTQ: {path}")
    return names


def validate(config, runtime, resolved):
    samples = load_samples(config)
    versions = {}
    commands = {"hisat2": ["--version"], "featureCounts": ["-v"], "samtools": ["--version"],
                "fastqc": ["--version"], "multiqc": ["--version"]}
    for tool, flags in commands.items():
        if not shutil.which(tool):
            raise ValueError(f"Missing {tool}; activate workflow/envs/tools.yaml or use bin/run-workflow")
        r = subprocess.run([tool, *flags], capture_output=True, text=True, timeout=30)
        versions[tool] = {"executable": shutil.which(tool), "version_output": (r.stdout + r.stderr).strip()}
    checks = {}
    for sid, row in samples.items():
        names = [prefix_names(row[k]) for k in ["fastq1", "fastq2"] if row[k]]
        if len(names) == 2 and names[0] != names[1]:
            raise ValueError(f"Read-pair IDs are not synchronized: {sid}")
        checks[sid] = {"prefix_records_checked": len(names[0]), "strandedness": row["strandedness"],
                       "layout": row["layout"], "files": {k: {"path": row[k],
                       "bytes": Path(row[k]).stat().st_size, "mtime_ns": Path(row[k]).stat().st_mtime_ns}
                       for k in ["fastq1", "fastq2"] if row[k]}}
    result = {"python": sys.version, "versions": versions, "samples": checks,
              "smoke": config["smoke"]["enabled"],
              "limitations": "No biological replicates; exploratory counts only. Prefix checks do not validate complete source files."}
    Path(runtime).parent.mkdir(parents=True, exist_ok=True)
    Path(runtime).write_text(json.dumps(result, indent=2) + "\n")
    Path(resolved).write_text(yaml.safe_dump(config, sort_keys=True))
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config-json", required=True)
    p.add_argument("--runtime", required=True)
    p.add_argument("--resolved", required=True)
    a = p.parse_args()
    print(json.dumps(validate(json.loads(a.config_json), a.runtime, a.resolved), indent=2))
