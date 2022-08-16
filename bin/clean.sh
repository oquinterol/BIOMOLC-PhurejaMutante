#!/bin/bash
. ./bin/var.sh # Variables unificadas
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
#find $DATA -iname "fasterq*" -type d -execdir rm -r {} \;
# Limpiar fastq completos
#find $DATA -iname "*.fastq" -type f -execdir rm {} \;
#find $DATA -iname "*.fq" -type f -execdir rm {} \;
#find $DATA -iname "*.fq.gz" -type f -execdir rm {} \;

#find $DATA -iname "*trimm*" -type f -execdir rm {} \;
#find $DATA -iname "*_val_*" -type f -execdir rm {} \;
# Limpiar los informes de fastqc
#find $DATA -iname "*fastqc*" -type f -not -path '*/raw/*' -execdir rm {} \;
# Limpiar el multiqc
#find $RESULT -iname "multiqc*" -type d -execdir rm -r {} \;
#find $RESULT -iname "multiqc*" -type f -execdir rm {} \;
# Mover las secuencias  de raw a principal
#mv data/fastq/raw/* data/fastq
# remover secuencias limpias
#rm data/fastq/*trimm*
# Quitar archivos sam
#find $SAM -iname "*.sam" -type f | parallel 'rm {}'

