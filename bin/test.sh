#!/bin/bash
DIR=$(pwd)
THD=$(($(nproc --all)-2))
RAM=$(($(awk '/MemTotal/ { printf "%.0f \n", $2/1024/1024 }' /proc/meminfo)-2))G
#Impresión de lo basico, para saber información basica del sistema.
echo 'Directorio: '$DIR
echo $DIR/data/fastq
echo '# de Nucleos: '$THD
echo 'Max. de RAM: '$RAM
