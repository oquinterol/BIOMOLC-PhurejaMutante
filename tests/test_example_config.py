"""Reusable templates validate with temporary inputs, never project data."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow/scripts"))
from pipeline_common import load_samples


class ExampleConfigTests(unittest.TestCase):
    def test_generic_template_is_valid_with_user_inputs(self):
        config = yaml.safe_load((ROOT / "config/examples/run.yaml").read_text())
        with (ROOT / "config/examples/samples.tsv").open(newline="") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for row in rows:
                # The parser validates paths; compression/content is checked later.
                (root / row["fastq1"]).touch()
            table = root / "samples.tsv"
            with table.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
                writer.writeheader()
                writer.writerows(rows)
            config.update(samples=str(table), data_root=str(root))
            samples = load_samples(config)
        self.assertEqual(set(samples), {"control_1", "mutant_1"})
        self.assertFalse(config["smoke"]["enabled"])
        self.assertFalse(config["allow_unconfirmed_library"])
        self.assertEqual(config["analysis"]["contrasts"], [])
        self.assertTrue(all(s["count_strand"] == 0 for s in samples.values()))


if __name__ == "__main__":
    unittest.main()
