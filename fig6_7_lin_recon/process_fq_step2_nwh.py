import sys
import os

import cassiopeia.ProcessingPipeline.process as process
#import cassiopeia.ProcessingPipeline.process.sequencing as sequencing
import pandas as pd 

import cassiopeia
import numpy as np

import tqdm
import argparse

## specify home dir and possorted genome bam from cellranger out

#home_dir = "/labs/congle/PRT/10X_analysis/prt_seq_v1/cr_count_te_untrimmed/tats_te_b5/outs"
#genome_bam = "/labs/congle/PRT/10X_analysis/prt_seq_v1/cr_count_te_untrimmed/tats_te_b5/outs/possorted_genome_bam.bam"

moltable = sys.argv[1]
out_fp = sys.argv[2]
out_dir = sys.argv[3]
cell_umi_thresh = sys.argv[4]

process.pickSeq(moltable, out_fp, out_dir, cell_umi_thresh=cell_umi_thresh, avg_reads_per_UMI_thresh=0, save_output=True)


