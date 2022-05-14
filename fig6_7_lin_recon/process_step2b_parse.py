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
import re

def main(input_path, output_path):
    
    homo_for = r"^TTTCCGG" # consider not enforcing this due to qual issues at the start of R2 that improve due to
    # increased seq diversity
    homo_rev = r"CAAA[ATCG]{10}GAATT" # must occur at the end of the line since there is an internal match! but this is 
                         # problematic because it filters out edited reads!!
    anchor = "ATCGATCGAT"
    anchor_qual = "IIIIIIIIII"
    new_lines = []
    
    with open(input_path, "r") as in_file:
        
        header = in_file.readline()
        #print(header)
        #new_lines.append(header)
        
        for line in in_file:
            
            line_strip = line.rstrip("\n")
        
            line_split = line_strip.split("\t")
            #print(len(line_split))
            
            seq = line_split[5]
            #seq_rc = str(Seq(line_split[5]).reverse_complement())
            #print(seq)
            qual = line_split[6]
            #print(qual)
            m = re.search(homo_for, seq)
            
            n = re.search(homo_rev, seq)
            
            if n: # only enforce reverse homology grep
                
                static_start = n.start() + 4
                static_end = n.end() - 5 # including the perturbation index 2020.09.08
                staticbc = seq[static_start:static_end]
                #print(staticbc)
                staticbc_qual = qual[static_start:static_end]
                
                bc_start = 0
                bc_end = n.start() + 4 
                dzy_bc = seq[bc_start:bc_end]
                dzy_bc_qual = qual[bc_start:bc_end]
                
                parse_seq = anchor + staticbc + dzy_bc
                parse_qual = anchor_qual + staticbc_qual + dzy_bc_qual
                
                new_line = line_split[0:5] + [parse_seq, parse_qual] + line_split[7:]
                #print(new_line)
                new_lines.append(new_line)
            

    in_file.close()
    
    with open(output_path, "w") as out_file:
        
        out_file.write(header)
        
        for new_line in new_lines:
            
            for data in new_line:
                
                out_file.write(data + "\t")
            
            out_file.write("\n")
    
    out_file.close()

def create_arg_parser():
    parser = argparse.ArgumentParser(description='parse picked sequences to only include dzy target sequences')
    parser.add_argument('input_path', metavar='N', help='folder path to picked seqs')
    parser.add_argument('output_path', metavar='N', help='folder path to output')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.input_path, parsed_args.output_path)
    



