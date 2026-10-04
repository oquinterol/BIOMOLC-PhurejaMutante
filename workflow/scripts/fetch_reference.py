#!/usr/bin/env python3
"""Download an HTTPS reference with optional pinned SHA-256 and atomic output."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.request


def fetch(url, output, expected_sha256=None):
    if not url.startswith("https://"):
        raise ValueError("Reference URL must use HTTPS")
    output = Path(output)
    if output.exists():
        if not expected_sha256:
            raise FileExistsError("An existing reference cache requires a pinned SHA-256")
        h = hashlib.sha256()
        with output.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                h.update(chunk)
        if h.hexdigest() != expected_sha256.lower():
            raise ValueError("Existing reference cache SHA-256 mismatch; refusing to replace it")
        return {"url": url, "sha256": h.hexdigest(), "bytes": output.stat().st_size,
                "checksum_pinned": True, "cache_revalidated": True}
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".download-", dir=output.parent)
    digest = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(fd, "wb") as target:
            with urllib.request.urlopen(url, timeout=120) as response:
                if not response.url.startswith("https://"):
                    raise ValueError("Refusing an insecure redirect")
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    target.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        checksum = digest.hexdigest()
        if not size:
            raise ValueError("Empty download")
        if expected_sha256 and checksum != expected_sha256.lower():
            raise ValueError(f"SHA-256 mismatch: expected {expected_sha256}, got {checksum}")
        os.replace(tmp, output)
    finally:
        Path(tmp).unlink(missing_ok=True)
    return {"url": url, "sha256": checksum, "bytes": size,
            "checksum_pinned": bool(expected_sha256)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url")
    p.add_argument("output")
    p.add_argument("--sha256")
    p.add_argument("--manifest", required=True)
    a = p.parse_args()
    result = fetch(a.url, a.output, a.sha256)
    Path(a.manifest).write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
