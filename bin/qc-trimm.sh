#!/bin/bash

# Variables
DIR=$(pwd)/data
DIRresults=$(pwd)/result
THD=$(($(nproc --all)-1))

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

## Verificar el contenido del arreglo
#for i in "${files[@]}"
#do
#	printf "Item\n"
#	printf "...........\n"
#	printf "...........\n"
#	echo $i
#	printf "...........\n"
#	printf "...........\n"
#done

# Recorre cada par de secuencias y se lo pasa a trim_galore
# --gzip option quitada para prueba
for i in "${files[@]}"
do
	printf "Limpiando secuencias.....\n"
	echo $i
	printf ".........................\n"
	printf ".........................\n"
	trim_galore \
		--paired \
		--q 30 \
		--cores $THD \
		--gzip \
		-o $DIR/fastq/trimm/ \
		$i
done

# Agregar paralelización de los informes FastQC para compilar con MultiQC
# haciendo uso de GNU parallel se puede generar un informe por hilo disponible con FastQC
# find $DIR/fastq -iname "*.fq.gz" -type f -print | parallel "fastqc --outdir $DIR/fastqc/ {}"

# usar la opcion de FastQC para mandarle todos los archivos
fastqc -o $DIR/fastqc -t $THD $DIR/fastq/*/*
# se compilan todos los informes usando MULTIQC
multiqc -o $DIRresults $DIR/fastqc
exit 0
