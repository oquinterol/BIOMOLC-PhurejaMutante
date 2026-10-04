"""Reference/config/count regressions; synthetic samples are not biological replicates."""
import csv
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workflow/scripts"))
from pipeline_common import load_samples
from prepare_reference import prepare, union_intervals
from summarize_counts import summarize, read_counts

GFF = """##gff-version 3
chr01\ttest\tmRNA\t1\t16\t.\t+\t.\tID=t1;Parent=g1
chr01\ttest\texon\t1\t5\t.\t+\t.\tParent=t1
chr01\ttest\texon\t11\t15\t.\t+\t.\tParent=t1
chr01\ttest\tmRNA\t1\t16\t.\t+\t.\tID=t2;Parent=g1
chr01\ttest\texon\t1\t6\t.\t+\t.\tParent=t2
chr01\ttest\texon\t11\t16\t.\t+\t.\tParent=t2
chr01\ttest\tmRNA\t21\t30\t.\t-\t.\tID=t3;Parent=g2
chr01\ttest\texon\t21\t30\t.\t-\t.\tParent=t3
"""


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.fasta = self.root / "genome.fa"
        self.fasta.write_text(">chr01\n" + "ACGT" * 10 + "\n")
        self.gff = self.root / "genes.gff3"
        self.gff.write_text(GFF)
        self.sample_table = self.root / "samples.tsv"
        self.source = self.root / "input.fastq"
        self.source.write_text("@r\nACGT\n+\nIIII\n")
        self.rows = [dict(sample_id=s, fastq1=str(self.source), fastq2="", layout="single",
                          strandedness="unstranded", stage="Flowering", genotype=s) for s in ["A", "B"]]
        self.write_samples()
        self.config = {"samples": str(self.sample_table), "data_root": str(self.root),
                       "smoke": {"enabled": False}, "allow_unconfirmed_library": False,
                       "reference": {"name": "synthetic-test"},
                       "analysis": {"mode": "exploratory", "pseudocount_cpm": 1,
                                    "contrasts": [{"name": "example", "numerator": "B", "denominator": "A"}]}}

    def write_samples(self):
        with self.sample_table.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(self.rows[0]), delimiter="\t")
            w.writeheader()
            w.writerows(self.rows)

    def test_exon_union_and_no_gene_rows(self):
        result = prepare(self.fasta, self.gff, self.root / "ref")
        self.assertEqual(result["gene_count"], 2)
        genes = list(csv.DictReader((self.root / "ref/genes.tsv").read_text().splitlines(), delimiter="\t"))
        self.assertEqual(genes[0]["exonic_length"], "12")
        self.assertEqual(genes[1]["exonic_length"], "10")
        self.assertIn("chr01\t4\t10\t+", (self.root / "ref/splice_sites.tsv").read_text())
        self.assertEqual(union_intervals([(1, 5), (3, 6), (6, 10), (20, 21)]), [[1, 10], [20, 21]])

    def test_smoke_keeps_complete_genes_only(self):
        result = prepare(self.fasta, self.gff, self.root / "ref", "chr01", 25)
        self.assertEqual(result["gene_count"], 1)
        self.assertTrue(result["smoke_reference"])
        self.assertEqual(result["sequences"], {"chr01": 25})
        self.assertNotIn("g2", (self.root / "ref/exons.saf").read_text())

    def test_annotation_chromosome_mismatch(self):
        self.gff.write_text(GFF.replace("chr01", "missing"))
        with self.assertRaisesRegex(ValueError, "coordinate mismatch"):
            prepare(self.fasta, self.gff, self.root / "ref")

    def test_annotation_out_of_bounds(self):
        self.gff.write_text(GFF.replace("\t21\t30\t", "\t21\t50\t"))
        with self.assertRaisesRegex(ValueError, "coordinate mismatch"):
            prepare(self.fasta, self.gff, self.root / "ref")

    def test_no_silent_cds_substitution(self):
        self.gff.write_text(GFF.replace("\texon\t", "\tCDS\t"))
        with self.assertRaisesRegex(ValueError, "No exon"):
            prepare(self.fasta, self.gff, self.root / "ref")

    def test_missing_transcript_parent(self):
        self.gff.write_text(GFF.replace("Parent=t1", "Parent=missing"))
        with self.assertRaisesRegex(ValueError, "Unknown exon Parent"):
            prepare(self.fasta, self.gff, self.root / "ref")

    def test_gff3_hash_mismatch(self):
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            prepare(self.fasta, self.gff, self.root / "ref", gff_sha="0" * 64)

    def test_unknown_strandedness_blocked_in_full_run(self):
        self.rows[0]["strandedness"] = "unknown"
        self.write_samples()
        with self.assertRaisesRegex(ValueError, "Confirm strandedness"):
            load_samples(self.config)
        self.config["allow_unconfirmed_library"] = True
        with self.assertRaisesRegex(ValueError, "only for technical smoke"):
            load_samples(self.config)
        self.config["smoke"]["enabled"] = True
        self.assertEqual(load_samples(self.config)["A"]["count_strand"], 0)

    def test_paired_layout_requires_two_files(self):
        self.rows[0]["layout"] = "paired"
        self.write_samples()
        with self.assertRaisesRegex(ValueError, "Layout/read-pair mismatch"):
            load_samples(self.config)

    def test_duplicate_sample_id(self):
        self.rows[1]["sample_id"] = "A"
        self.write_samples()
        with self.assertRaisesRegex(ValueError, "Duplicate sample"):
            load_samples(self.config)

    def test_cross_stage_contrasts_rejected(self):
        self.rows[1]["stage"] = "Meristem"
        self.write_samples()
        with self.assertRaisesRegex(ValueError, "same stage"):
            load_samples(self.config)

    def test_no_differential_mode(self):
        self.config["analysis"]["mode"] = "differential"
        with self.assertRaisesRegex(ValueError, "exploratory"):
            load_samples(self.config)

    def write_counts(self, sid, values):
        p = self.root / "counts"
        p.mkdir(exist_ok=True)
        (p / f"{sid}.tsv").write_text("# featureCounts test\nGeneid\tChr\tStart\tEnd\tStrand\tLength\tinput.bam\n" + "".join(f"g{i+1}\tchr01\t1\t5\t+\t5\t{v}\n" for i, v in enumerate(values)))
        (p / f"{sid}.tsv.summary").write_text(f"Status\tinput.bam\nAssigned\t{sum(values)}\nUnassigned_Unmapped\t100\n")

    def test_cpm_and_ratios_are_descriptive(self):
        self.write_counts("A", [10, 30])
        self.write_counts("B", [30, 10])
        report = summarize(self.config, self.root / "counts", self.root / "tables")
        self.assertEqual(report["assigned_exonic_units"], {"A": 40, "B": 40})
        rows = list(csv.DictReader((self.root / "tables/cpm.tsv").read_text().splitlines(), delimiter="\t"))
        self.assertEqual(float(rows[0]["A"]), 250000)
        ratios = list(csv.DictReader((self.root / "tables/descriptive_ratios.tsv").read_text().splitlines(), delimiter="\t"))
        self.assertAlmostEqual(float(ratios[0]["log2_cpm_ratio"]), math.log2(750001/250001))
        self.assertFalse(any("pvalue" in k or "padj" in k for k in ratios[0]))
        self.assertEqual(report["analysis_mode"], "exploratory")

    def test_zero_library_not_normalized_to_fake_zero(self):
        self.write_counts("A", [0, 0])
        self.write_counts("B", [5, 10])
        report = summarize(self.config, self.root / "counts", self.root / "tables")
        self.assertEqual(report["zero_libraries"], ["A"])
        rows = list(csv.DictReader((self.root / "tables/cpm.tsv").read_text().splitlines(), delimiter="\t"))
        self.assertEqual(rows[0]["A"], "NA")

    def test_assigned_summary_must_match_matrix(self):
        self.write_counts("A", [1, 2])
        self.write_counts("B", [2, 1])
        (self.root / "counts/A.tsv.summary").write_text("Status\tinput.bam\nAssigned\t99\n")
        with self.assertRaisesRegex(ValueError, "matrix total"):
            summarize(self.config, self.root / "counts", self.root / "tables")

    def test_gene_lengths_must_match_samples(self):
        self.write_counts("A", [1, 2])
        self.write_counts("B", [2, 1])
        p = self.root / "counts/B.tsv"
        p.write_text(p.read_text().replace("\t5\t2\n", "\t6\t2\n"))
        with self.assertRaisesRegex(ValueError, "lengths differ"):
            summarize(self.config, self.root / "counts", self.root / "tables")


if __name__ == "__main__":
    unittest.main()
