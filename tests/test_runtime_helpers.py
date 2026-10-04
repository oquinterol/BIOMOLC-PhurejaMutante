"""Safety/provenance regressions without network or system changes."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "workflow/scripts"
sys.path.insert(0, str(SCRIPTS))
from fetch_reference import fetch
from pipeline_common import load_samples
from validate_inputs import prefix_names


class Response(io.BytesIO):
    url = "https://example.org/reference.gz"


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_download_hash_validation(self):
        payload = b"reference data"
        out = self.root / "ref.gz"
        with patch("fetch_reference.urllib.request.urlopen", return_value=Response(payload)):
            result = fetch(Response.url, out, hashlib.sha256(payload).hexdigest())
        self.assertEqual(out.read_bytes(), payload)
        self.assertTrue(result["checksum_pinned"])
        self.assertEqual(list(self.root.glob(".download-*")), [])

    def test_download_mismatch_leaves_no_output(self):
        out = self.root / "ref.gz"
        with patch("fetch_reference.urllib.request.urlopen", return_value=Response(b"wrong")):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                fetch(Response.url, out, "0" * 64)
        self.assertFalse(out.exists())
        self.assertEqual(list(self.root.glob(".download-*")), [])

    def test_existing_cache_revalidated_without_network(self):
        out = self.root / "ref.gz"
        out.write_bytes(b"reference")
        with patch("fetch_reference.urllib.request.urlopen") as network:
            result = fetch(Response.url, out, hashlib.sha256(b"reference").hexdigest())
        network.assert_not_called()
        self.assertTrue(result["cache_revalidated"])

    def test_existing_bad_cache_preserved(self):
        out = self.root / "ref.gz"
        out.write_bytes(b"original")
        with self.assertRaisesRegex(ValueError, "refusing to replace"):
            fetch(Response.url, out, "0" * 64)
        self.assertEqual(out.read_bytes(), b"original")

    def test_insecure_reference_url_rejected(self):
        with self.assertRaisesRegex(ValueError, "HTTPS"):
            fetch("http://example.org/file", self.root / "ref")

    def test_prefix_mate_ids_normalized(self):
        left, right = self.root / "R1.fastq", self.root / "R2.fastq.gz"
        left.write_text("@r/1\nACGT\n+\nIIII\n")
        with gzip.open(right, "wt") as f:
            f.write("@r/2\nTGCA\n+\nIIII\n")
        self.assertEqual(prefix_names(left), prefix_names(right))

    def test_malformed_quality_rejected(self):
        src = self.root / "input.fastq"
        src.write_text("@r\nACGT\n+\nI II\n")
        with self.assertRaisesRegex(ValueError, "Malformed"):
            prefix_names(src)

    def test_nonfinite_pseudocount_rejected(self):
        for value in [float("nan"), float("inf"), 0, -1]:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "finite and positive"):
                load_samples({"analysis": {"mode": "exploratory", "pseudocount_cpm": value},
                              "smoke": {"enabled": True}})

    def test_replace_flag_refreshes_only_derived_output(self):
        source, output = self.root / "input.fastq", self.root / "subset.fastq.gz"
        source.write_text("@r\nACGT\n+\nIIII\n")
        output.write_bytes(b"old derived output")
        before = source.read_bytes()
        r = subprocess.run([sys.executable, str(SCRIPTS / "subset_fastq.py"), str(source),
                            str(output), "--reads", "1", "--replace-workflow-output"],
                           capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(source.read_bytes(), before)
        self.assertEqual(gzip.decompress(output.read_bytes()), before)
        self.assertEqual(json.loads(r.stdout)["output"], str(output.resolve()))

    def test_replace_flag_cannot_replace_original(self):
        source = self.root / "input.fastq"
        source.write_text("@r\nACGT\n+\nIIII\n")
        before = source.read_bytes()
        r = subprocess.run([sys.executable, str(SCRIPTS / "subset_fastq.py"), str(source),
                            str(source), "--replace-workflow-output"],
                           capture_output=True, text=True, timeout=10)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
