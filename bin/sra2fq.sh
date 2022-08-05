#!/bin/bash
#Zona de Variables
DIR=$(pwd)/data
THD=$(($(nproc --all)-1))
RAM=$(($(awk '/MemTotal/ { printf "%.0f \n", $2/1024/1024 }' /proc/meminfo)-2))G
# Ejecución
# Faster-dump herramienta mas reciente
find $DIR/sra -iname "*.sra" -type f -execdir \
	fasterq-dump \
		--threads $THD \
		--mem $RAM \
		--outdir $DIR/fastq {} \;

# Otra idea que tengo es usar fastq-dump que me permite mas flags
#find . -iname "*.sra" -type f -execdir \
#	parallel-fastq-dump \
#		--gzip \
#		--threads $THD \
#		--skip-technical \
#		--split-files \
#		--read-filter pass \
#		--outdir $DIR/fastq/ {} \;

# Renombrado de todas las secuencias quitando el sra por R
# asi se puede determinar el forward and reverse
find $DIR/fastq -iname "*fastq" -type f -execdir rename .sra_ _R {} \;
