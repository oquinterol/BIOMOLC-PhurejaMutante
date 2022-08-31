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

# Detectar la distro, para saber que gestor de paquetes usar.
echo "Detectando Distro Linux"

printf "\nPrimer script busca archivos especificos a cada distro\n"
# Fedora/RHEL/CentOS distro
 if [ -f /etc/redhat-release ]; then
    echo "FED"
# Debian/Ubuntu
elif [ -r /lib/lsb/init-functions ]; then
    echo "DEB"
elif [ -f /etc/arch-release ]; then
  echo "ARCH"
fi
printf "\n"
## Otra prueba de script
printf "Segundo script de prueba usa /etc/os-release\n"
DISTRIB=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
if [[ ${DISTRIB} = "Ubuntu"* ]]; then
	if uname -a | grep -q '^Linux.*Microsoft'; then
		# ubuntu via WSL Windows Subsystem for Linux
		echo "Windows Subsystem for Linux"
	else
		# Native Ubuntu
		echo "Ubuntu"
	fi
elif [[ ${DISTRIB} = '"Debian"'* ]]; then
	echo "Debian"
elif [[ ${DISTRIB} = '"Pop!_OS"'* ]]; then
	echo "Pop! OS"
fi

# Este archivo es el que me va a servir
printf "\nEste archivo es el que va a servir, probar con maquinas virtuales /etc/os-release\n"
printf "Pues al filtrar nos daria algo como esto: "$(awk -F= '/^NAME/{print $2}' /etc/os-release)"\n"
