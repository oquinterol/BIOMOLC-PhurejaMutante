#!/bin/bash

. ./bin/var.sh # Variables unificadas

# Lee todos los archivos el la carpeta data/fastq
# y los guarda en un arreglo
for archivo in $FQRAW/*.fq.gz; do
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
		-o $FQTRIM \
		$i
done

# Renombrado de todas las secuencias quitando el _1_ por _
find $FQTRIM -iname "*val*.fq.gz" -type f -execdir \
	rename _1_ _ {} \;
find $FQTRIM -iname "*val*.fq.gz" -type f -execdir \
    rename _2_ _ {} \;

printf "Generando informes de secuencias.....\n"
# usar la opcion de FastQC para mandarle todos los archivos
fastqc -o $FASTQC -t $THD $FASTQ/*/*
# se compilan todos los informes usando MULTIQC
multiqc -o $RESULT $FASTQC
exit 0
