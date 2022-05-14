# copy specific chunks of code needed for this step

import sys
import os
import pandas as pd 
import numpy as np
#from tqdm import tqdm
from pathlib import Path
#import bokeh.palettes
import time
#import matplotlib.pyplot as plt
import subprocess
import argparse

SCLT_PATH = "/home/nwhughes/Cassiopeia/cassiopeia"

def convert_sam_to_bam(sam_input, bam_output):
    """
    Converts a SAM file to BAM file.

    :param sam_input:
        Sam input file 
    :param bam_output:
        File path to write the bam output.
    :return:
        None.
    """

    cmd = "samtools view -S -b " + sam_input + " > " + bam_output

    os.system(cmd)

def main(alignments, ref, output, context=True):
    """
    Given many alignments, we extract the indels by comparing the CIGAR strings in the alignments to the reference sequence. 

    :param alignments:
        Alignments provided in SAM or BAM format.
    :param ref:
        File path to the reference seqeunce, assumed to be a FASTA.
    :param output:
        Output file path.
    :param context:
        Include sequence context around indels.
    :return:
        None
    """

    perl_script = (SCLT_PATH + '/ProcessingPipeline/process/callAlleles_dzy4T.pl') # need to modify for tats config
    cmd = "perl " + str(perl_script) + " " + alignments + " " + ref + " " + output
    if context:
        cmd += " --context"

    cmd += " > _log.stdout 2> _log.stderr"

    p = subprocess.Popen(cmd, shell=True)
    pid, ecode = os.waitpid(p.pid, 0)

    bam_file = str(Path(output).with_suffix(".bam"))

    convert_sam_to_bam(output, bam_file)

def create_arg_parser():
    parser = argparse.ArgumentParser(description='binarize states encoded by cpf1-induced indels')
    parser.add_argument('alignments', metavar='N', help='folder path to alignments (1)')
    parser.add_argument('ref', metavar='N', help='folder path to reference sequence (2)')
    parser.add_argument('out', metavar='N', help='folder path to output (3)')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.alignments, parsed_args.ref, parsed_args.out)
    



