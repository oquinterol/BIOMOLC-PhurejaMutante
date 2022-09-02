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

# Detectando Distro
echo "Acceso sudo para instalar dependecias"
sudo clear
echo "Detectando la distribucion Linux"
sleep 1s
DISTRIB=$(awk -F= '/^NAME/{print $2}' /etc/os-release)
echo "La Distribución es $DISTRIB"
sleep 2s

# Verifica el gestor paquetes existente
if [[ -f /usr/bin/apt ]];
then
	echo "Usando apt para descargar dependencias"
	sleep 1s
	sudo apt -y update
	# Paquete FastQC y Gestor de paquetes pip de python3 entre otras...
	sudo apt install -y tree build-essential fastqc python3-pip pigz gzip samtools bcftools bwa bowtie2 r-base firefox parallel 
	# Usando pip para instalar cutadapt y multiqc y otras
	# python3 -m pip install --user --upgrade cutadapt
	python3 -m pip install cutadapt multiqc HTSeq biopython
	# Instalacion librerias R
	echo "La instalacion liberias R"
	sudo Rscript ./bin/r-paquetes.r

elif [[ -f /usr/bin/pacman ]]; 
then
	echo "Usando pacman para descargar dependencias"
	sleep 1s
	# Repositorios Oficiales
	sudo pacman --noconfirm -Syy tree python-pip base-devel fastqc yay r firefox parallel
	# Usando AUR para descargar los paquetes
	yay --noconfirm -Syy samtools bcftools bwa pigz gzip
	# Python pip instala paquetes faltantes
	pip install cutadapt multiqc HTSeq biopython
	# Instalacion librerias R
	echo "La instalacion liberias R"
	Rscript ./bin/r-paquetes.r
fi
# Instalación de TrimGalore
if [[ -f ~/.local/bin/trim_galore ]];
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
	find $DIR -iname "trim_galore*" -not -path '*/bin/*' -exec rm -r {} \;
	find $DIR -iname "TrimGalore*" -not -path '*/bin/*' -exec rm -r {} \;
	echo "TrimGalore! Instalado en el PATH para el usuario ~/.local/bin"
fi

# Exportando el PATH del usuario para hacer disponibles los programas al usuario
if [[ -f /usr/bin/zsh ]];
then
	echo '# PATH para pipeline Phureja y paquetes python pip' >> $HOME/.zshrc
	echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.zshrc
elif [[ -f /usr/bin/bash ]];
then
	echo '# PATH para pipeline Phureja y paquetes python pip ' >> $HOME/.bashrc
	echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
fi

# Descarga de los datos de Referencia (Phujera) SpudDB
# Ejemplo -j le dice cuentos trabajos se pueden paralelizar
#cat url.list | parallel -j 8 wget -O {#}.html {}
echo "Descargando las secuencias de referencia de SpudDB"
cd $FASTA
cat $DATA/referencefiles.txt | parallel wget -N {}
cd $DIR

echo "Instalacion finalizada, ya se puede hacer uso del pipeline"
echo "Cierra esta terminal y abre una nueva para cargar los cambios"