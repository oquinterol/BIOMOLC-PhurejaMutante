# Modulos del pipline

install:
	./bin/install.sh
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
dea:
	./bin/dea.sh
clean:
	./bin/clean.sh
