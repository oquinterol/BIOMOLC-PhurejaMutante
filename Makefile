# Modulos del pipline
result: dea snp
	
dea: bamsort
	./bin/dea.sh
	./bin/dea-r.r
snp: bamsort
	./bin/snpcall.sh
bamsort: sam2bam
	./bin/bamsort.sh ./data/bam/sort/*.bam
sam2bam: align
	./bin/sam2bam.sh ./data/bam/*.bam
align: trim
	./bin/align.sh 
trim: sra2fq
	./bin/trim.sh
qctrim: trim
	./bin/qc-trim.sh 
qcraw: sra2fq 
	./bin/qc-raw.sh
sra2fq: ./data/sra/*.sra
	./bin/sra2fq.sh
install: 
	chmod ug+x ./bin/*
	./bin/install.sh
