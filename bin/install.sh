#!/bin/bash
# Crear las carpetas
# .
# ├── bin
# ├── data
# │	  ├── bam
# │	  │	  └── sort
# │   ├── dea
# │	  ├── fasta
# │	  ├── fastq
# │	  │	  ├── raw
# │	  │	  └── trim
# │	  ├── fastqc
# │	  │	  ├── raw
# │	  │	  └── trim
# │	  ├── sam
# │	  ├── sra
# │	  └── vcf
# ├── docs
# └── result
#     └── report
#         ├── both
#         └── raw
mkdir -p ./{bin,data/{bam/sort,dea,fasta,fastq/{raw,trim},fastqc/{raw,trim},sam,sra,vcf},docs,result/report/{raw,both}}
# Cargar las variables de directorios
DIR=$(pwd)
DATA=$DIR/data
FASTQC=$DATA/fastqc
FASTQ=$DATA/fastq
FQRAW=$FASTQ/raw
FQTRIM=$FASTQ/trim
FASTA=$DATA/fasta
BAM=$DATA/bam
SAM=$DATA/sam
SRA=$DATA/sra
VCF=$DATA/vcf
RESULT=$DIR/result
REPORT=$RESULT/report
QCRAW=$REPORT/raw
QCTRIM=$REPORT/trim
# Descarga de los datos de Referencia (Phujera) SpudDB
# Ejemplo
#cat url.list | parallel -j 8 wget -O {#}.html {}
echo "Descargando las secuencias de referencia de SpudDB"
cd $FASTA
cat $DATA/referencefiles.txt | parallel wget -N {}
cd $DIR
# Detectando Distro
printf "Detectando la distribucion Linux\n"
DISTRIB=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
if [[ ${DISTRIB} == *"Ubuntu"* ]] || [[ ${DISTRIB} == *"Debian"* ]] || [[ ${DISTRIB} == *"Pop!_OS"* ]];
then
	echo "Usando apt para descargar dependencias"
elif [[ ${DISTRIB} == *"Manjaro"* ]] || [[ ${DISTRIB} == *"Arch"* ]]; then
	echo "Usando pacman para descargar dependencias"
fi

if [[ -f ~/.local/bin/trim_galore ]]
then
	echo "trim_galore esta instalado en su sistema"
else
	# Instalación de TrimGalore
	# Descarga del repo
	curl -fsSL https://github.com/FelixKrueger/TrimGalore/archive/refs/tags/0.6.7.tar.gz -o trim_galore.tar.gz
	# Descompresion
	tar xvzf trim_galore.tar.gz
	# busca el script y lo mueve al bin del repo
	find $DIR -iname "trim_galore" -type f -not -path '*/bin/*' -exec mv {} ~/.local/bin/ \;
	# Borramos los datos de instalación
	find $DIR \(-iname "trim_galore*" -o -iname "TrimGalore*" \) -not -path '*/bin/*' -exec rm -r {} \;
fi