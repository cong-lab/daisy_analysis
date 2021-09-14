#!/bin/bash

dirpath=`readlink -f $1`

for d in ${dirpath}/*/
do
	dirname=`basename $d`
	for f in ${d}*.fastq.gz
	do
		b=`basename $f`
		name=${b/.fastq.gz/}
		echo -e "${name},${f}" >> "${dirname}_designfq_list_gz.csv"
	done
done
