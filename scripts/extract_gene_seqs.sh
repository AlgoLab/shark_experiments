#!/bin/bash

#
# This script requires: samtools (tested with 1.9), bedops (tested
# with 2.4.37) and bedtools (tested with 2.29.0, it doesn't work with
# 2.17.0)
#
# HOWTO: bash extract_gene_seqs.sh {reference.fa} {genes.gtf} {flanking_size} > {genes.fa}
#
# Output to STDOUT
#

in_fa=$1      # reference (fasta)
in_gtf=$2     # annotation (gtf)
flreg_size=$3 # flanking region size

uid=$$

fa_bed=/tmp/${uid}.fa.bed
gtf_tid=/tmp/${uid}.gtf.tid
bed_1=/tmp/${uid}.bed.1
bed_2=/tmp/${uid}.bed.2

# Index fasta
if [ ! -f "${in_fa}.fai" ]; then
    samtools faidx ${in_fa}
fi

# Fasta to bed (length)
awk 'BEGIN {FS="\t"}; {print $1 FS $2}' ${in_fa}.fai > ${fa_bed}

# Adds transcript_id to gtf records
awk '{{ if ($0 ~ "transcript_id") print $0; else print $0" transcript_id \"\";"; }}' ${in_gtf} > ${gtf_tid}

# GTF to BED (only genes)
gtf2bed < ${gtf_tid} | grep -P "\tgene\t" > ${bed_1}

# Adds flanking regions
bedtools slop -i ${bed_1} -g ${fa_bed} -b ${flreg_size} > ${bed_2}

# BED to FASTA
bedtools getfasta -name -fi ${in_fa} -bed ${bed_2} | fold -w 80

# Clean up
rm ${fa_bed} ${gtf_tid} ${bed_1} ${bed_2}
