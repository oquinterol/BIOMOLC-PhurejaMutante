# Modulos del pipline (Documentar)

sra2fq: sra/*.sra
	./bin/sra2fq.sh sra/
index: fasta/*.fq
	./bin/bwa-index.sh fasta/
bwa-mem: fasta/*.fa fasta/*.fq
	./bin/bwa-mem.sh
trimm: fasta/*.fq
	./bin/qc-trimm.sh fasta/*.qc
