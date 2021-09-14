#!/bin/bash

dirpath=`readlink -f $1`

for f in ${dirpath}/*.fa
do
b=`basename $f`
name=${b/.fa/}
echo -e "${name},${f}"
done
