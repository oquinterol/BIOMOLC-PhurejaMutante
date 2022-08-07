#!/bin/bash

# Variables
DIR=$(pwd)/data
DIRresults=$(pwd)/result
THD=$(($(nproc --all)-2))

# Ejemplo sencillo de limpieza de lecturas pareadas
# trim_galore \
#	--paired \
#	--q 30 \
#	--gzip \
#	--fastqc \
#	SRR######_1.fastq.gz \
#	SRR######_2.fastq.gz \
#	-o trimm_files/
#

# Lee todos los archivos el la carpeta data/fastq
# y los guarda en un arreglo
for archivo in $DIR/fastq/raw/*.fq.gz; do
  arreglo+=( "${archivo}" )
done
#for para comprobar el arreglo con los datos de la carpeta RAW
#for i in "${arreglo[@]}"
#do
#	echo 'Termino por separado'
#	echo $i
#done
# Concatenar los dos archivos en uno para pasarlos al trimm
cont=$((${#arreglo[@]}-1))
x=0
while [ $x -le $cont ]
do
	files+=("${arreglo[$x]}"" ""${arreglo[$x+1]}")
	x=$(( $x + 2 ))
done
# Se desfaza el contador con el total de items en el arreglo
# Pues uno inicia en 1 i el otro en 0

#echo 'Verificacion de files'
#echo ' '
#for i in "${files[@]}"
#do
#        echo 'Termino por separado'
#        echo $i
#done

# Recorre cada par de secuencias y se lo pasa a trim_galore
for i in "${files[@]}"
do
	trim_galore \
		--paired \
		--q 30 \
		--cores $THD \
		--gzip \
		--fastqc \
		--fastqc_args "--outdir $DIR/fastqc" \
		-o $DIR/fastq/trimm/ \
		$i
done
