#!/bin/bash

. ./bin/var.sh # Variables unificadas

# Lee todos los archivos el la carpeta data/fastq y los guarda en un arreglo
# Guarda los nombres de archivos .sam
for file in $SAM/*.sam; do
  samF+=( "${file##*/}" )
done

# Captura del ID
for nameid in "${samF[@]}"; do
    id+=(${nameid%%.*})
done
echo 'Convirtiendo secuencias .sam a .bam'
echo '...................................'
# Convertir SAM a BAM archivo por archivo
#for ((c=0; c<=$((${#id[@]}-1)); c++)); do
#    samtools view -S -b $SAM/${samF[$c]} > $BAM/${id[$c]}.bam
#done
# Implementacion usando GNU-parallel
find $SAM -iname "*.sam" -print | parallel 'samtools view -S -b {} > {}.bam'
# Renombrar los archivos
find $SAM -iname "*.bam" -execdir rename .sam.bam .bam {} \;
# Mover archivos bam a la carpeta correspondiente
find $SAM -iname "*.bam" -execdir  mv {} $BAM \;

# Guarda los nombres de archivos .bam
for file in $BAM/*.bam; do
  bamF+=( "${file##*/}" )
done
echo 'Ordenando secuencias .bam'
echo '...................................'
# Ordenar los archivos bam
#for ((c=0; c<=$((${#id[@]}-1)); c++)); do
#    samtools sort $BAM/${bamF[$c]} -o $BAM/${id[$c]}_sorted.bam
#done
# implementación con GNU-parallel
find $BAM -type f \( -iname "*.bam" ! -iname "*sorted*" \) -print | parallel \
'samtools sort {} -o {}_sorted.bam'
find $SAM -iname "*.bam" -execdir rename .bam_ _ {} \;

exit 0
