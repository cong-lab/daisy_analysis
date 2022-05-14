#!/bin/bash

module purge
module load miniconda
module load samtools

python3.6 process_fq_nwh.py

