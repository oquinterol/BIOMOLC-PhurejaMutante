"""Dependency-free tests for safe extraction of technical FASTQ fixtures."""
import gzip
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "workflow/scripts/subset_fastq.py"
spec = importlib.util.spec_from_file_location("subset_fastq", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

FASTQ = b"@r1\nACGT\n+\nIIII\n@r2\nTGCA\n+\nJJJJ\n"


class SubsetFastqTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.fastq.gz"
        self.output = self.root / "subset.fastq.gz"
        with gzip.open(self.source, "wb") as f:
            f.write(FASTQ)

    def test_bounded_subset_preserves_source(self):
        before = self.source.read_bytes()
        result = module.subset_fastq(self.source, self.output, 1)
        self.assertEqual(result["reads"], 1)
        self.assertEqual(result["read_lengths"], [4])
        self.assertEqual(gzip.decompress(self.output.read_bytes()), FASTQ.split(b"@r2")[0])
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(result["subset_sha256"], hashlib.sha256(self.output.read_bytes()).hexdigest())

    def test_plain_input_and_short_file(self):
        source = self.root / "plain.fastq"
        source.write_bytes(FASTQ)
        result = module.subset_fastq(source, self.output, 10)
        self.assertEqual(result["reads"], 2)
        self.assertEqual(gzip.decompress(self.output.read_bytes()), FASTQ)

    def test_refuses_overwrite(self):
        self.output.write_bytes(b"existing")
        with self.assertRaises(FileExistsError):
            module.subset_fastq(self.source, self.output, 1)
        self.assertEqual(self.output.read_bytes(), b"existing")

    def test_refuses_output_symlink(self):
        self.output.symlink_to(self.root / "absent")
        with self.assertRaises(FileExistsError):
            module.subset_fastq(self.source, self.output, 1)
        self.assertFalse((self.root / "absent").exists())

    def test_refuses_input_as_output(self):
        before = self.source.read_bytes()
        with self.assertRaises(FileExistsError):
            module.subset_fastq(self.source, self.source, 1)
        self.assertEqual(self.source.read_bytes(), before)

    def test_invalid_records_leave_no_output(self):
        for bad in [b"", b"@r\nACGT\n+\nIII\n", b"r\nACGT\n+\nIIII\n",
                    b"@r\nACGT\n+\n", b"@r\nACGT\n+\nI I!\n", b"@r\n\n+\n\n"]:
            with self.subTest(record=bad):
                with gzip.open(self.source, "wb") as f:
                    f.write(bad)
                with self.assertRaises(ValueError):
                    module.subset_fastq(self.source, self.output, 1)
                self.assertFalse(self.output.exists())
                self.assertEqual(list(self.root.glob(".fastq-subset-*")), [])

    def test_positive_limit_required(self):
        for limit in [0, -1]:
            with self.assertRaises(ValueError):
                module.subset_fastq(self.source, self.output, limit)
        self.assertFalse(self.output.exists())

    def test_deterministic_gzip(self):
        other = self.root / "other.fastq.gz"
        module.subset_fastq(self.source, self.output, 1)
        module.subset_fastq(self.source, other, 1)
        self.assertEqual(self.output.read_bytes(), other.read_bytes())

    def test_missing_input(self):
        with self.assertRaises(FileNotFoundError):
            module.subset_fastq(self.root / "missing", self.output, 1)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
