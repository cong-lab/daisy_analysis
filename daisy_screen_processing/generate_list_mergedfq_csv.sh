#!/bin/bash

dirpath=`readlink -f $1`

for f in ${dirpath}/*.extendedFrags.fastq.gz
do
b=`basename $f`
name=${b/.extendedFrags.fastq.gz/}
echo -e "${name},${f}"
# f2=${f/R1/R2}
# echo -e "${name},${f},${f2}"
done
