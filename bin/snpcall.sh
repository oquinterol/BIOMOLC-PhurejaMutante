#!/bin/bash

. ./bin/var.sh # Variables unificadas

## Volver a indexar la secuencia referencia haciendo uso de samtools No soporta gz horrible

samtools faidx $TREF

## Generar archivo raw de VCF Variant Call format todo los archivos ordenados sorted.bam
#samtools mpileup -g -f my.fasta my-sorted-1.bam my-sorted-n.bam > my-raw.bcf
# Arreglo con todos los sorted.bam
for file in $BAM/*_sorted.bam; do
  bamFS+=( "${file##*/}" )
done
# Se crea el VCF file
cd $BAM
samtools mpileup -f $TREF -s "${bamFS[@]}" > $VCF/$SNPname-raw.bcf
cd $DIR

for file in $VCF/*-raw.bcf; do
  vfcraw+=( "${file##*/}" )
done
# Call SNPs
bcftools view -vcg $VCF/*raw.bcf > $VCF/$SNPname-call.bcf
# Filtrado de SNPs
bcftools view $VCF/$SNPname-call.bcf | vcfutils.pl varFilter - > $VCF/$SNPname.vcf

exit 0