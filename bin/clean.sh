#!/bin/bash
DIR=$(pwd)
dataclean=(fastq fastqc)
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
find $DIR/data/ -iname "fasterq*" -type d -execdir rm -r {} \;
# Limpiar fastq completos
find $DIR/data/ -iname "*.fastq" -type f -execdir rm {} \;
