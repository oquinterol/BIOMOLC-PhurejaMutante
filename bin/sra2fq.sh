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
		--outdir $DIR/fastq/raw {} \;

# Otra idea que tengo es usar GNU-parallel permite lanzar todos los procesos al tiempo
# Pero al realizar la prueba, parallel le toma 41 m 37s y con el for toma 20m 13s
# cd $DIR/fastq
# find $DIR/sra -iname "*.sra" \
# -type f | parallel \
# 'fasterq-dump --outdir raw {}'
# cd $DIR
# Renombrado de todas las secuencias quitando el sra
find $DIR/fastq/raw -iname "*.fastq" -type f -execdir \
	rename .sra_ _ {} \;
find $DIR/fastq/raw -iname "*.fastq" -type f -execdir \
        rename .fastq .fq {} \;

#echo 'Comprimiendo Secuencias....'
# Compresion de todas las secuencias usando gzip
find $DIR/fastq/raw -iname "*.fq" -type f -execdir pigz -k -p$THD {} \;
exit 0
