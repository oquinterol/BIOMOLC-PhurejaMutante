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
samtools mpileup -f $TREF "${bamFS[@]}" -o $VCF/$SNPname-raw.bcf

for file in $VCF/*-raw.bam; do
  vfcraw+=( "${file##*/}" )
done
# Call SNPs
bcftools view -bvcg $VCF/${vfcraw[0]} > $VCF/$SNPname.bcf
# Filtrado de SNPs
bcftools view $VCF/$SNPname.bcf | vcfutils.pl varFilter - > $SNPname-final.bcf
