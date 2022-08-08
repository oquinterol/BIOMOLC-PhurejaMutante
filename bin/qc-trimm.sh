#!/bin/bash

# Variables
DIR=$(pwd)/data
DIRresults=$(pwd)/result
THD=$(($(nproc --all)-2))

# Lee todos los archivos el la carpeta data/fastq
# y los guarda en un arreglo
for archivo in $DIR/fastq/raw/*.fq.gz; do
  arreglo+=( "${archivo}" )
done

# Concatenar los dos archivos en un solo string para pasarlos al trimm
cont=$((${#arreglo[@]}-1))
x=0
while [ $x -le $cont ]
do
	files+=("${arreglo[$x]}"" ""${arreglo[$x+1]}")
	x=$(( $x + 2 ))
done

# Recorre cada par de secuencias y se lo pasa a trim_galore
for i in "${files[@]}"
do
	trim_galore \
		--paired \
		--q 30 \
		--cores $THD \
		--gzip \
		-o $DIR/fastq/trimm/ \
		$i
done
# Agregar paralizacioón de los informes FastQC para compilar con MultiQC
exit 0
