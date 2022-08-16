#!/bin/bash

. ./bin/var.sh # Variables unificadas

# Primer paso crear cuantificar los datos por lectura para esto es hace uso de el archivo .sorted.bam
# ejemplo
#samtools view MT1/Tophat_Out/accepted_hits.sorted.bam | python \ -m
#HTSeq.scripts.count -q -s no - ~/Indexes/Mus_musculus/UCSC/mm10/Genes/genes.gtf >
#MT1/MT1.count.txt

# estructura
#samtools view XXXXXXXXX_sorted.bam | htseq-count -q -s no - XXXXXXX.gff3.gz > XXXXX.txt

samtools view $SAM/SRR18272798.sam | htseq-count --idattr=Parent -s no - $AREF > ${id[0]}.txt

#--quantMode geneCounts