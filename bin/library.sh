#!/bin/bash
DIR=$(pwd)

# Pequeña lista de los programas que uso.
# - FastQC
# - cutadapt
# - sra-tools
# - TrimGalore (Automatic detetection)
# Instalacion de fastqc

# Instalacion de python and pip

# Instalación de cutadapt
python3 -m pip install --user --upgrade cutadapt
# Instalación de TrimGalore
# Descarga del repo
curl -fsSL https://github.com/FelixKrueger/TrimGalore/archive/refs/tags/0.6.7.tar.gz -o trim_galore.tar.gz
# Descompresion
tar xvzf trim_galore.tar.gz
# busca el script y lo mueve al bin del repo
find $DIR -iname "trim_galore" \
	-type f -not -path '*/bin/*' \
	-exec mv {} ~/.local/bin/ \;
# Borramos los datos de instalación
find $DIR \(-iname "trim_galore*" -o -iname "TrimGalore*" \) \
	-not -path '*/bin/*' \
	-exec rm -r {} \;
# Pide instalar el paquete pigz (Trim con multihilo)

# Instalacion de SRAtoolkit
