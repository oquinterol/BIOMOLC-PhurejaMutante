#!/bin/bash
# Lista y metodos de instalación de todas las librerias necesarias para correr los analis
# Primero necesito conda, y que con conda puedo instalar las herramientas de SRA
# Primero herramienta de paralelizacion de fastq-dump
# https://github.com/rvalieris/parallel-fastq-dump
# Tambien instala  sra desde conda
conda install -c bioconda parallel-fastq-dump
## Preferiblemente usar pip los pinches PATH son un estress
python3 -m pip install --user --upgrade cutadapt
conda install cutadapt
