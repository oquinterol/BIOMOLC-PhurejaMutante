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
cat $DATA/files.txt | parallel wget -N {}
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

echo $DISTRIB