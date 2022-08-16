# Modulos del pipline (Documentar)


test:
	./bin/test.sh
sra2fq:
	./bin/sra2fq.sh
trimm:
	./bin/qc-trimm.sh
align:
	./bin/align.sh
	./bin/sam2bam.sh
clean:
	./bin/clean.sh
