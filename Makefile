# Modulos del pipline (Documentar)

test:
	./bin/test.sh
sra2fq:
	./bin/sra2fq.sh
trimm:
	./bin/qc-trimm.sh

index: fasta/*.fq
	./bin/bwa-index.sh fasta/
bwa-mem: fasta/*.fa fasta/*.fq
	./bin/bwa-mem.sh

clean:
	./bin/clean.sh
