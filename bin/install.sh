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
echo "Acceso sudo para instalar dependecias"
sudo clear
echo "Detectando la distribucion Linux"
DISTRIB=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
echo "La Distribución es $DISTRIB"
# Verifica si el gestor paquetes existe
if [[ -f /usr/bin/apt ]];
then
	echo "Usando apt para descargar dependencias"
	sudo apt update
	# Paquete FastQC y Gestor de paquetes pip de python3 entre otras...
	sudo apt install build-essential fastqc python3-pip pigz gzip samtools bcftools bwa bowtie2 r-base firefox parallel 
	# Usando pip para instalar cutadapt y multiqc
	# python3 -m pip install --user --upgrade cutadapt
	python3 -m pip install cutadapt multiqc HTSeq biopython

elif [[ -f /usr/bin/pacman ]]; then
	echo "Usando pacman para descargar dependencias"
	
fi
# Instalación de TrimGalore
if [[ -f ~/.local/bin/trim_galore ]]
then
	echo "trim_galore esta instalado en su sistema"
else
	# Descarga del repo
	curl -fsSL https://github.com/FelixKrueger/TrimGalore/archive/refs/tags/0.6.7.tar.gz -o trim_galore.tar.gz
	# Descompresion
	tar xvzf trim_galore.tar.gz
	# busca el script y lo mueve al bin del repo
	find $DIR -iname "trim_galore" -type f -not -path '*/bin/*' -exec mv {} ~/.local/bin/ \;
	# Borramos los datos de instalación
	find $DIR \(-iname "trim_galore*" -o -iname "TrimGalore*" \) -not -path '*/bin/*' -exec rm -r {} \;
	echo "TrimGalore! Instalado en el PATH para el usuario"
fi

# Instalacion librerias R
echo "La instalacion liberias R"
Rscript ./bin/r-paquetes.R
