#!/bin/bash
. ./bin/var.sh # Variables unificadas
printf "Generando informes de secuencias.....\n"
# usar la opcion de FastQC para mandarle todos los archivos
fastqc -o $FASTQC/raw -t $THD $FASTQ/raw/*
# se compilan todos los informes usando MULTIQC
multiqc -o $QCRAW $FASTQC/raw
printf "Abriendo informe en Firefox.....\n"
firefox $QCRAW/multiqc_report.html 
exit 0