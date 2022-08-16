# Modulos del pipline


test:
	./bin/test.sh
sra2fq:
	./bin/sra2fq.sh
trimm:
	./bin/qc-trimm.sh
align:
	./bin/align.sh
	./bin/sam2bam.sh
snp:
	./bin/snpcall.sh


clean:
	./bin/clean.sh
