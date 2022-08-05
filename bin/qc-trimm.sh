#!/bin/bash
for i in *.fq;
do RQC-parallel-qc -i "{$i}" -t 14 -o ../data/;
done
 
