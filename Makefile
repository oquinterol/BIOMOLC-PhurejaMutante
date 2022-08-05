# Modulos del pipline (Documentar)

test:
	./bin/test.sh
sra2fq:
	./bin/sra2fq.sh

index: fasta/*.fq
	./bin/bwa-index.sh fasta/
bwa-mem: fasta/*.fa fasta/*.fq
	./bin/bwa-mem.sh
trimm: fasta/*.fq
	./bin/qc-trimm.sh fasta/*.qc
clean:
	./bin/clean.sh
