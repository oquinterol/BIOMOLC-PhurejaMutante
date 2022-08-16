#!/bin/sh
# Ubicaciones
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
#Secuencias de Referencia
TREFz=$FASTA/DM_1-3_516_R44_potato.v6.1.hc_gene_models.cdna.fa.gz
TREF=$FASTA/DM_1-3_516_R44_potato.v6.1.hc_gene_models.cdna.fa
GREF=$FASTA/DM_1-3_516_R44_potato_genome_assembly.v6.1.fa.gz
AREF=$FASTA/DM_1-3_516_R44_potato.v6.1.hc_gene_models.gff3.gz
AREFwb=$FASTA/PGSC_DM_v3.4_gene.gff
#Capacidad de computo
THD=$(($(nproc --all)-1)) # Hilos disponibles en la maquina
RAM=$(($(awk '/MemTotal/ { printf "%.0f \n", $2/1024/1024 }' /proc/meminfo)-1))G #Cantidad de RAM disponible en la maquina
#ID de los archivos sra
for file in $SRA/*.sra; do
  sraF+=( "${file##*/}" )
done
# Captura del ID
for nameid in "${sraF[@]}"; do
    id+=(${nameid%%.*})
done

# Nombres
SNPname='HojavsTuberculo'

