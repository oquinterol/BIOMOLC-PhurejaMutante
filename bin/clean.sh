#!/bin/bash
DIR=$(pwd)
datos=$(pwd)/data
result=$(pwd)/result
#dataclean=(fastq fastqc)
# Prueba con un While
#let CONTADOR=0
#while [ $CONTADOR -lt ${#dataclean[*]} ]
#do
#	printf "${ORANGE}$pad$pad$pad$pad$pad$pad$pad ${dataclean[CONTADOR]}${NC}\n"
#	find  $DIR/data/${dataclean[CONTADOR]} -iname "*${dataclean[CONTADOR]}*" -type f -execdir rm {} \;
#
#	let CONTADOR=CONTADOR+1
#done

# Paso a paso
# Limpiar partes incompletas de sra2fq
#find $datos -iname "fasterq*" -type d -execdir rm -r {} \;
# Limpiar fastq completos
#find $datos -iname "*.fastq" -type f -execdir rm {} \;
# Limpiar los informes de fastqc
find $datos -iname "*fastqc*" -type f -not -path '*/raw/*' -execdir rm {} \;
# Limpiar el multiqc
find $result -iname "multiqc*" -type d -execdir rm -r {} \;
find $result -iname "multiqc*" -type f -execdir rm {} \;
# Mover las secuencias  de raw a principal
mv data/fastq/raw/* data/fastq
# remover secuencias limpias
rm data/fastq/*trimm*
