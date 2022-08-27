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


#Parte de R
library(“DESeq2”)
sample.names <- sort(paste(c(“MT”, “WT”), rep(1:3, each=2), sep=““))
file.names <- paste(“../”, sample.names, “/”, sample.names, “.count.txt”, sep=““)
conditions <- factor(c(rep(“MT”, 3), rep(“WT”, 3)))
sampleTable <- data.frame(sampleName=sample.names,
fileName=file.names,
condition=conditions)
# Leemos la cuantificacion que hicimos en el paso anterior
ddsHTSeq<-DESeqDataSetFromHTSeqCount(sampleTable=sampleTable, directory=“.”,design=~ condition )
# Corremos el analisis
ddsHTSeq <- ddsHTSeq[rowSums(counts(ddsHTSeq)) > 10, ]
dds <-DESeq(ddsHTSeq)
# Revision de calidad
rld <- rlogTransformation(dds, blind=FALSE)
# grafica PCA
plotPCA(rld, intgroup=“condition”, ntop=nrow(counts(ddsHTSeq)))

# Grafica heatmap de correlacion
cU <-cor( as.matrix(assay(rld)))
cols <- c( “dodgerblue3”, “firebrick3” )[condition]
heatmap.2(cU, symm=TRUE, col= colorRampPalette(c(“darkblue”,”white”))(100), 
    labCol=colnames(cU), labRow=colnames(cU),
    distfun=function(c) as.dist(1 - c), trace=“none”, Colv=TRUE, 
    cexRow=0.9, cexCol=0.9, key=F, font=2,
    RowSideColors=cols, ColSideColors=cols)

