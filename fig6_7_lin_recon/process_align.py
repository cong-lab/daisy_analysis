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
edna_mat_path = "/oak/stanford/scg/lab_congle/PRT/Miseq_20210313_PE75/2_align/EDNAFULL.modified"
SAM_HEADER_TATS = "@HD	VN:1.3\n@SQ	SN:dzy_4t_135	LN:98" # this is really bad to hardcode the header -- MAKE SURE TO MOD IF REF CHANGES!!!!!

def collapseDF2Fastq(data_fp, out_fp):
    """
    Collapses a DataFrame to a FASTQ file.

    :param data_fp:
        Dataframe input file.
    :param out_fp:
        Filepath for output FASTQ file.
    :return:
        None.
    """

    perl_script = (SCLT_PATH + "/ProcessingPipeline/process/collapseDF2fastq.pl")
    cmd = "perl " + str(perl_script) + " " + data_fp + " " + out_fp

    p = subprocess.check_output(cmd, shell=True)


def main(ref, queries, outfile, matrix_path, gapopen=13, gapextend=0.5, ref_format="fasta", query_format="fastq", out_format="sam"):
    """
    Aligns many queries to a single reference sequence using EMBOSS water. By default, we assume the reference is in FASTA format, the queries 
    are all in FASTQ format, and that the output format will be a SAM file. The output file is automatically written.

    :param ref:
        File path to the reference sequence.
    :param queries:
        Queries, provided as a dataframe output from the `pickSeq` function. This will automatically be converted to a FASTQ file.
    :param gapopen:
        Gap open penalty.
    :param gapextend:
        Gap extension penalty.
    :param ref_format:
        Format of reference sequence.
    :param query_format:
        Format of query seqeunces.
    :param out_format:
        Output file format.
    :return:
        None. 
    """

    queries_fastq = str(Path(queries).with_suffix(".fastq"))
    collapseDF2Fastq(queries, queries_fastq) 
    
    #queries_fastq = queries # modifed due to need to pre-process picked seqs due to recombination

    cmd = "water -asequence " + ref + " -sformat1 " + ref_format  + " -bsequence " + queries_fastq + " -sformat2 " + query_format + " -gapopen " + str(gapopen) + " -gapextend " + str(gapextend) + " -outfile " + outfile + " -aformat3 " + out_format + " -datafile " + matrix_path
    #print(cmd)
    cmd = cmd.split(" ")
    
    subprocess.check_output(cmd)

    with open(outfile, "r+") as f: #the file appears to be writing twice
        content = f.read()
        f.seek(0,0)
        f.write(SAM_HEADER_TATS + "\n" + content)
        f.write(content)

def create_arg_parser():
    parser = argparse.ArgumentParser(description='binarize states encoded by cpf1-induced indels')
    parser.add_argument('ref', metavar='N', help='folder path to reference fasta (1)')
    parser.add_argument('query', metavar='N', help='folder path to query picked seqs (2)')
    parser.add_argument('out', metavar='N', help='folder path to output (3)')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.ref, parsed_args.query, parsed_args.out, edna_mat_path)
    



