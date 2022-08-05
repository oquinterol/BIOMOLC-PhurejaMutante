#!/bin/bash 
# Convert Fastq to Fasta
for i in *.fq;
do sed -n '1~4s/^@/>/p;2~4p' "${i}" > "${i%.*}.fa";
done

# index fasta files
for i in  *.fa; 
do bwa index bwa index "${i}"; 
done
