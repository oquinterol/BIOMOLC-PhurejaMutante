"""Alignment neutrality must not silently change library counting orientation."""
import csv
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow/scripts"))
from pipeline_common import alignment_strandness, load_samples


class AlignmentStrandTests(unittest.TestCase):
    def test_default_single_end_options(self):
        self.assertEqual(alignment_strandness({"layout": "single", "strandedness": "forward"}, {}), "F")
        self.assertEqual(alignment_strandness({"layout": "single", "strandedness": "reverse"}, {}), "R")

    def test_default_paired_end_options(self):
        self.assertEqual(alignment_strandness({"layout": "paired", "strandedness": "forward"}, {}), "FR")
        self.assertEqual(alignment_strandness({"layout": "paired", "strandedness": "reverse"}, {}), "RF")

    def test_neutral_alignment_omits_strand_option(self):
        for layout in ["single", "paired"]:
            for strand in ["forward", "reverse"]:
                self.assertIsNone(alignment_strandness({"layout": layout, "strandedness": strand},
                                  {"alignment": {"use_strandedness": False}}))

    def test_unknown_and_unstranded_have_no_option(self):
        for strand in ["unknown", "unstranded"]:
            self.assertIsNone(alignment_strandness({"layout": "single", "strandedness": strand}, {}))

    def sample_config(self, root, alignment):
        read = root / "sample.fastq"
        read.write_text("@r1\nA\n+\nI\n")
        table = root / "samples.tsv"
        with table.open("w", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(["sample_id", "fastq1", "fastq2", "layout", "strandedness", "stage", "genotype"])
            writer.writerow(["s1", str(read), "", "single", "reverse", "Flowering", "g1"])
        return {"samples": str(table), "analysis": {"mode": "exploratory"},
                "smoke": {"enabled": False}, "alignment": alignment}

    def test_neutral_alignment_preserves_reverse_counting(self):
        with tempfile.TemporaryDirectory() as d:
            config = self.sample_config(Path(d), {"use_strandedness": False})
            self.assertEqual(load_samples(config)["s1"]["count_strand"], 2)

    def test_nonboolean_alignment_choice_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            config = self.sample_config(Path(d), {"use_strandedness": "false"})
            with self.assertRaisesRegex(ValueError, "must be boolean"):
                load_samples(config)

    def test_nonmapping_alignment_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            config = self.sample_config(Path(d), False)
            with self.assertRaisesRegex(ValueError, "must be a mapping"):
                load_samples(config)


if __name__ == "__main__":
    unittest.main()
