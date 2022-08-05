#!/bin/bash
for i in  *.sra; do fastq-dump --slipt-spot --include-technical"${i}" ;done
