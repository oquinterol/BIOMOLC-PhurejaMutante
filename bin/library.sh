#!/bin/bash
# Lista y metodos de instalación de todas las librerias necesarias para correr los analis
# Primero necesito conda, y que con conda puedo instalar las herramientas de SRA
# Primero herramienta de paralelizacion de fastq-dump
# https://github.com/rvalieris/parallel-fastq-dump
# Tambien instala  sra desde bioconda
conda install -c bioconda parallel-fastq-dump
conda install cutadapt
