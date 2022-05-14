import sys
import os

import cassiopeia.ProcessingPipeline.process as process
import pandas as pd 

import cassiopeia
import numpy as np
import tqdm


## specify home dir and possorted genome bam from cellranger out

#home_dir = "/labs/congle/PRT/10X_analysis/prt_seq_v1/cr_count_te_untrimmed/tats_te_b5/outs"
#genome_bam = "/labs/congle/PRT/10X_analysis/prt_seq_v1/cr_count_te_untrimmed/tats_te_b5/outs/possorted_genome_bam.bam"

ref = sys.argv[1]
queries = sys.argv[2]
outfile = sys.argv[3]

process.align_sequences(ref, queries, outfile)


