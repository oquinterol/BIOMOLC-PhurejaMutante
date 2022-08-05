#!/bin/bash

DIR=$(pwd)/data
DIRresults=$(pwd)/result

# Lo primero es generar un informe fastqc para cada secuencia, para ver el antes.
find $DIR -iname "*.fastq" -type f -execdir fastqc -o $DIR/fastqc {} \;
# Se compila todos los informes
multiqc -o $DIRresults/before $DIR/fastqc

# Se remueve los adaptadores y las lecturas de baja calidad
# Primero se remueven adaptores


