# read in mt table and assign static tags to cells to create lgs
# main filter parameters are readCounts and num UMIs / lg within assigned to a cell

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
from collections import defaultdict
import csv
import itertools
from Levenshtein import distance as lev
from tqdm.notebook import tqdm
from time import sleep

def main(in_mt, assign_vect_fp, out_fp):
    
    in_mt_df = pd.read_csv(in_mt, index_col = 0, sep = "\t")
    #print(in_mt_df)
    
    assign_vect = pd.read_csv(assign_vect_fp, index_col = 0)
    
    with tqdm(total=len(assign_vect)) as pbar:
        
        for cell, lg in assign_vect.iteritems():

            #print(cell)
            in_mt_df.loc[cell, "lineageGrp"] = lg
            pbar.update(1)
            sleep(1)
    
    #print(in_mt_df)
    
    in_mt_df.to_csv(out_fp)
    
def create_arg_parser():
    parser = argparse.ArgumentParser(description='assign cells to lgs')
    parser.add_argument('in_mt', metavar='N', help='in molecular table where alleles are assigned to cells')
    parser.add_argument('assign_vect_fp', metavar='N', help='vector with lgs identified through hclustering')
    parser.add_argument('out_fp', metavar='N', help='path to output allele table for lin recon')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.in_mt, parsed_args.assign_vect_fp, parsed_args.out_fp)
    
    
    
    
    