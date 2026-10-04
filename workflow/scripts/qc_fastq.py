#!/usr/bin/env python3
"""Run FastQC using stable per-sample output names without altering input reads."""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--input", required=True)
p.add_argument("--name", required=True)
p.add_argument("--outdir", required=True)
p.add_argument("--log", required=True)
a = p.parse_args()
out = Path(a.outdir).resolve()
out.mkdir(parents=True, exist_ok=True)
source = Path(a.input).resolve()
suffix = ".fastq.gz" if source.suffix == ".gz" else ".fastq"
Path(a.log).parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix=".fastqc-", dir=out) as tmp:
    link = Path(tmp) / (a.name + suffix)
    link.symlink_to(source)
    with open(a.log, "w") as log:
        subprocess.run(["fastqc", "--threads", "1", "--outdir", str(out), str(link)],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
