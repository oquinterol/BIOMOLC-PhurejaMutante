#!/bin/bash

. ./bin/var.sh # Variables unificadas

# Cuantificacion de la expresion
samtools view $SAM/SRR18272798.sam | htseq-count --idattr=Parent -s no - $AREF > ${id[0]}.txt
