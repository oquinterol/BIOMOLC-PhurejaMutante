#!/usr/bin/env python3
"""Validate FASTA/GFF3, union gene exons into SAF and export splice junctions."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import unquote


def text_open(path):
    return gzip.open(path, "rt") if str(path).endswith(".gz") else open(path)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def attributes(value):
    result = {}
    for part in value.split(";"):
        if not part:
            continue
        if "=" not in part:
            raise ValueError("Expected standard GFF3 key=value attributes, not GTF/bare IDs")
        key, val = part.split("=", 1)
        result[key] = [unquote(x) for x in val.split(",")]
    return result


def union_intervals(intervals):
    merged = []
    for start, end in sorted(set(intervals)):
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(end, merged[-1][1])
    return merged


def prepare(fasta, gff, outdir, contig=None, max_bases=None, fasta_sha=None, gff_sha=None):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    checksums = {"fasta": sha256(fasta), "gff3": sha256(gff)}
    for label, expected in [("fasta", fasta_sha), ("gff3", gff_sha)]:
        if expected and checksums[label] != expected:
            raise ValueError(f"{label} SHA-256 mismatch")
    if bool(contig) != bool(max_bases) or (max_bases is not None and max_bases < 1):
        raise ValueError("Smoke reference requires both a contig and a positive max_bases")
    lengths = {}
    selected = {}
    current = None
    with text_open(fasta) as source, (out / "genome.fa").open("w") as target:
        for line in source:
            if line.startswith(">"):
                current = line[1:].split()[0]
                if current in lengths:
                    raise ValueError(f"Duplicate FASTA sequence: {current}")
                lengths[current] = 0
                if not contig or current == contig:
                    selected[current] = 0
                    target.write(f">{current}\n")
            elif line.strip():
                if current is None:
                    raise ValueError("Sequence before FASTA header")
                seq = line.strip()
                lengths[current] += len(seq)
                if current in selected:
                    remain = max_bases - selected[current] if contig else len(seq)
                    seq = seq[:max(0, remain)]
                    if seq:
                        target.write(seq + "\n")
                        selected[current] += len(seq)
    if not selected or not all(selected.values()):
        raise ValueError("Requested FASTA region not found or empty")
    transcripts = {}
    exons = []
    with text_open(gff) as f:
        for n, line in enumerate(f, 1):
            if line.startswith("##FASTA"):
                break
            if not line.strip() or line.startswith("#"):
                continue
            row = line.rstrip("\n").split("\t")
            if len(row) != 9:
                raise ValueError(f"Malformed GFF3 line {n}")
            chrom, _, kind, start, end, _, strand, _, attr = row
            if kind not in {"mRNA", "transcript", "exon"}:
                continue
            start, end = int(start), int(end)
            if chrom not in lengths or start < 1 or end < start or end > lengths[chrom]:
                raise ValueError(f"Annotation/FASTA coordinate mismatch at line {n}")
            if strand not in {"+", "-"}:
                raise ValueError(f"Unknown exon/transcript strand at line {n}")
            a = attributes(attr)
            if kind in {"mRNA", "transcript"}:
                if len(a.get("ID", [])) != 1 or len(a.get("Parent", [])) != 1:
                    raise ValueError("Each transcript must have one ID and one gene Parent")
                tid, gid = a["ID"][0], a["Parent"][0]
                if tid in transcripts:
                    raise ValueError(f"Duplicate transcript: {tid}")
                # SpudDB intentionally has gene Parent IDs without explicit gene rows.
                transcripts[tid] = (gid, chrom, start, end, strand)
            else:
                if not a.get("Parent"):
                    raise ValueError("Exon lacks transcript Parent")
                exons.append((chrom, start, end, strand, a["Parent"]))
    if not exons:
        raise ValueError("No exon features: CDS cannot be silently substituted for exons")
    loci = {}
    for gid, chrom, start, end, strand in transcripts.values():
        if gid not in loci:
            loci[gid] = [chrom, start, end, strand]
        else:
            loc = loci[gid]
            if (chrom, strand) != (loc[0], loc[3]):
                raise ValueError(f"Gene {gid} spans different contigs/strands")
            loc[1], loc[2] = min(loc[1], start), max(loc[2], end)
    keep = {g for g, (c, s, e, st) in loci.items() if c in selected and e <= selected[c]}
    gene_exons = {}
    transcript_exons = {}
    for chrom, start, end, strand, parents in exons:
        for tid in parents:
            if tid not in transcripts:
                raise ValueError(f"Unknown exon Parent transcript: {tid}")
            gid, tc, ts, te, st = transcripts[tid]
            if (tc, st) != (chrom, strand) or start < ts or end > te:
                raise ValueError(f"Exon outside transcript {tid}")
            if gid in keep:
                gene_exons.setdefault(gid, []).append((start, end))
                transcript_exons.setdefault(tid, []).append((start, end))
    if not gene_exons:
        raise ValueError("No complete exon-annotated genes in selected reference")
    with (out / "exons.saf").open("w", newline="") as f, (out / "genes.tsv").open("w", newline="") as g:
        w, gw = csv.writer(f, delimiter="\t"), csv.writer(g, delimiter="\t")
        w.writerow(["GeneID", "Chr", "Start", "End", "Strand"])
        gw.writerow(["gene_id", "chrom", "start", "end", "strand", "exonic_length"])
        for gid in sorted(gene_exons):
            chrom, start, end, strand = loci[gid]
            intervals = union_intervals(gene_exons[gid])
            for left, right in intervals:
                w.writerow([gid, chrom, left, right, strand])
            gw.writerow([gid, chrom, start, end, strand, sum(e - s + 1 for s, e in intervals)])
    junctions = set()
    for tid, intervals in transcript_exons.items():
        _, chrom, _, _, strand = transcripts[tid]
        spans = union_intervals(intervals)
        for (_, left_end), (right_start, _) in zip(spans, spans[1:]):
            junctions.add((chrom, left_end - 1, right_start - 1, strand))
    with (out / "splice_sites.tsv").open("w") as f:
        for row in sorted(junctions):
            f.write("\t".join(map(str, row)) + "\n")
    manifest = {"source_fasta": str(Path(fasta).resolve()), "source_gff3": str(Path(gff).resolve()),
                "sha256": checksums, "gene_count": len(gene_exons), "splice_sites": len(junctions),
                "sequences": selected, "smoke_reference": bool(contig),
                "counting_unit": "union of annotated exons grouped by transcript Parent gene ID"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fasta", required=True)
    p.add_argument("--gff3", required=True)
    p.add_argument("--outdir", required=True)
    p.add_argument("--contig")
    p.add_argument("--max-bases", type=int)
    p.add_argument("--fasta-sha256")
    p.add_argument("--gff3-sha256")
    a = p.parse_args()
    print(json.dumps(prepare(a.fasta, a.gff3, a.outdir, a.contig, a.max_bases,
                             a.fasta_sha256, a.gff3_sha256), indent=2))
