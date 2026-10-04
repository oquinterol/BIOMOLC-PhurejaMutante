#!/usr/bin/env python3
"""Copy a bounded FASTQ prefix for smoke tests, never for biological inference."""

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import tempfile


def subset_fastq(source, output, max_reads=10000):
    """Validate/copy up to max_reads records; refuse to overwrite any output.

    Only the copied prefix is validated, not the original file's full integrity.
    Four-line FASTQ is required. Plain and gzip input are supported; output is gzip.
    """
    source, output = Path(source), Path(output)
    if max_reads < 1:
        raise ValueError("max_reads must be positive")
    if not source.is_file():
        raise FileNotFoundError(source)
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if source.resolve() == output.resolve():
        raise ValueError("Input and output must differ")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".fastq-subset-", dir=output.parent)
    count = 0
    lengths = set()
    try:
        opener = gzip.open if source.suffix == ".gz" else open
        with os.fdopen(fd, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as target:
                with opener(source, "rb") as reads:
                    for record in range(1, max_reads + 1):
                        header = reads.readline()
                        if not header:
                            break
                        sequence, plus, quality = (reads.readline() for _ in range(3))
                        lines = [line.rstrip(b"\r\n") for line in (header, sequence, plus, quality)]
                        h, s, p, q = lines
                        if (not h.startswith(b"@") or not p.startswith(b"+")
                                or not s or len(s) != len(q)
                                or any(base < 33 or base > 126 for base in q)):
                            raise ValueError(f"Invalid four-line FASTQ record {record}")
                        target.write(b"\n".join(lines) + b"\n")
                        lengths.add(len(s))
                        count += 1
        if count == 0:
            raise ValueError("Input contains no FASTQ records")
        # Atomic publication without replacing an existing file, even on a race.
        os.link(temporary, output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    digest = hashlib.sha256()
    with output.open("rb") as data:
        for chunk in iter(lambda: data.read(1024 * 1024), b""):
            digest.update(chunk)
    return {
        "source": str(source.resolve()), "output": str(output.resolve()),
        "reads": count, "read_lengths": sorted(lengths),
        "subset_sha256": digest.hexdigest(),
        "scope": "FASTQ prefix only; technical smoke test, not biological inference",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reads", type=int, default=10000)
    parser.add_argument("--replace-workflow-output", action="store_true",
                        help="Atomically refresh a derived workflow output, never the input")
    args = parser.parse_args()
    try:
        if args.replace_workflow_output:
            if args.source.resolve() == args.output.resolve():
                raise ValueError("Input and output must differ")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix=".subset-", dir=args.output.parent) as tmp:
                result = subset_fastq(args.source, Path(tmp) / "subset.fastq.gz", args.reads)
                os.replace(result["output"], args.output)
                result["output"] = str(args.output.resolve())
        else:
            result = subset_fastq(args.source, args.output, args.reads)
    except (OSError, ValueError, EOFError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
