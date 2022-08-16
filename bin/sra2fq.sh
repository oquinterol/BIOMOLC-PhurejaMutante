#!/bin/sh

. ./bin/var.sh # Variables unificadas

# Ejecución
# Faster-dump herramienta mas reciente
find $SRA -iname "*.sra" -type f -execdir \
	fasterq-dump \
		--threads $THD \
		--mem $RAM \
		--outdir $FQRAW {} \;
# Renombrado de todas las secuencias quitando el sra
find $FQRAW -iname "*.fastq" -type f -execdir \
	rename .sra_ _ {} \;
find $FQRAW -iname "*.fastq" -type f -execdir \
        rename .fastq .fq {} \;
echo 'Comprimiendo Secuencias....'
# Compresion de todas las secuencias usando gzip
find $FQRAW -iname "*.fq" -type f -execdir pigz -k -p$THD {} \;
exit 0
