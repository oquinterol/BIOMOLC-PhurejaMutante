#!/bin/bash
. ./bin/var.sh # Variables unificadas
printf "Generando informes de secuencias filtradas.....\n"
# usar la opcion de FastQC para mandarle todos los archivos
fastqc -o $FASTQC/trim -t $THD $FASTQ/trim/*
# se compilan todos los informes usando MULTIQC
multiqc -o $QCRAW $FASTQC/
printf "Abriendo informe en Firefox.....\n"
firefox $QCRAW/multiqc_report.html 
exit 0