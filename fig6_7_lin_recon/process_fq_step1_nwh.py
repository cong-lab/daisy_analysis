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

home_dir = sys.argv[1]
print(home_dir)
bam_path = sys.argv[2]
print(bam_path)

process.collapseUMIs(home_dir, bam_path, force_sort=True, show_progress=True) 


