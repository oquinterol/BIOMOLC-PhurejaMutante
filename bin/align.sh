#!/bin/bash
# recordar que esto es para paired-end
# Primero toca generar un indice del genoma que se tenga de referencia
## bwa index my.fasta --> my.fasta==Genoma de referencia
# Segundo hacer el alinemaminto, primero se crea un archivo .sai esto se hace por cada secuencia.
## bwa aln ref.fa -b1 my_1.fastq > 1.sai
## bwa aln ref.fa -b2 my_2.fastq > 2.sai
# Tercero producir el archivo .sam 
# bwa sampe ref.fa 1.sai 2.sai my_1.fastq my_2.fastq > aln.sam

