#!/bin/bash

dirpath=`readlink -f $1`

for f in ${dirpath}/*.extendedFrags.fastq.gz
do
b=`basename $f`
name=${b/.extendedFrags.fastq.gz/}
zgrep -onP "T{6}G[ATCG]{13}TTT[ATCG]" ${f} > ${name}".bcgrep.txt"
# f2=${f/R1/R2}
# echo -e "${name},${f},${f2}"
done

mkdir bc_grep_list
mv *.bcgrep.txt bc_grep_list
