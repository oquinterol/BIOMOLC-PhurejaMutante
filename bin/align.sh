#!/bin/bash
. ./bin/var.sh # Variables unificadas
# recordar que esto es para paired-end
# Primero toca generar un indice de las secuencias que se tengan de referencia
## bwa index my.fasta --> my.fasta == Seciencia de referencia
bwa index $TREF
# Lee todos los archivos el la carpeta data/fastq y los guarda en un arreglo
# Guarda los nombres de forward
for file in $FQTRIM/*1.fq.gz; do
  filesF+=( "${file##*/}" )
done
# Guarda los nombres de reverse
for file in $FQTRIM/*2.fq.gz; do
  filesR+=( "${file##*/}" )
done
# Captura del ID
for nameid in "${filesF[@]}"; do
    id+=(${nameid%%_*})
done
# Correr el bwa mem para todas las secuenias pareadas 
for ((c=0; c<=$((${#id[@]}-1)); c++))
do
    bwa mem $TREF -t $THD $FQTRIM/${filesF[$c]} $FQTRIM/${filesR[$c]} > $SAM/${id[$c]}.sam
done

# Con un pipe | Pasar de una vez bam