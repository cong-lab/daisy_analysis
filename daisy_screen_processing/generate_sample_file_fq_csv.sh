#!/bin/bash

dirpath=`readlink -f $1`

for f in ${dirpath}/*_1.fq.gz
do
b=`basename $f`
name=${b/_1.fq.gz/}
f2=${f/_1/_2}
echo -e "${name},${f},${f2}"
done
