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

def main(in_mt, read_thresh, umi_thresh, cell_thresh, meta_dict_out_fp, out_fp):
    
    in_df = pd.read_csv(in_mt, index_col = 0, sep = "\t")
    static_tags = list(set(in_df["intBC"]))
    cellBCs = list(set(in_df.index))
    
    static_df = pd.DataFrame(index = static_tags, columns = cellBCs).fillna(0)
    
    sub_df = in_df[["UMI", "intBC", "readCount"]]
    read_thresh_df = sub_df[sub_df["readCount"] >= int(read_thresh)]
    
    for cellbc, row in read_thresh_df.iterrows():
        
        UMI = row["UMI"]
        static_tag = row["intBC"]
        static_df.loc[static_tag, cellbc] += 1
    
    # series with number of UMIs mapping to a static tag
    static_tag_umi_sum = static_df.sum(axis = 1)
    
    # now generate a whitelist of static tags based on umi representation 
    
    drop_lst = []
    
    all_combos = itertools.combinations(list(static_tag_umi_sum.index), 2)
    
    for combo in all_combos:
        
        seq_1 = combo[0]
        seq_2 = combo[1]
        
        dist = lev(seq_1, seq_2)
        
        if dist <= 2:
            
            sum_1 = static_tag_umi_sum[seq_1]
            sum_2 = static_tag_umi_sum[seq_2]
            
            if sum_1 > sum_2:
                
                drop_lst.append(seq_2)
                
            elif sum_2 > sum_1:
                
                drop_lst.append(seq_1)
    
    static_df.drop(drop_lst) # remove problematic static tags!

    cell_lg_dict = defaultdict(list)
    
    cells = list(static_df)
    
    for cell in cells:
        
        #print(cell)
        cell_soi = static_df[cell]
        cell_soi_filter = cell_soi[cell_soi >= int(umi_thresh)]
        filtered_static_tags = tuple(sorted(list(cell_soi_filter.index)))
        cell_lg_dict[filtered_static_tags].append(cell)
        
    print(cell_lg_dict)
    
    final_dict = {}
    
    i = 0
    
    meta_dict = {} # this dictionary will store the lg id (index) and then the static-tags that call it for cross-time ref
    
    for static_tag_lst, cellbc_lst in cell_lg_dict.items():
        
        num_cells = len(cellbc_lst)
        
        if num_cells >= int(cell_thresh):
            
            final_dict[str(i)] = cellbc_lst
            static_tag_list = list(static_tag_lst)
            static_tag_list.append(str(num_cells)) # last entry in list is the number of cells within the lg
            meta_dict[str(i)] = static_tag_list
            i += 1
    
    #print(final_dict)
    
    # write metadict to file for interpretation
    
    print(meta_dict)
    with open(meta_dict_out_fp, "w") as metafile:
        
        writer = csv.writer(metafile)
        for key in sorted(meta_dict.keys()):
            if meta_dict[key] is not None: # only write lgs that have static tags 
            
                writer.writerow([key] + meta_dict[key])
    
    
    
    for lg, cellbc_lst in final_dict.items():
        
        for cell in cellbc_lst:
            
            in_df.loc[cell, "lineageGrp"] = lg
            
    in_df.to_csv(out_fp)
    
def create_arg_parser():
    parser = argparse.ArgumentParser(description='assign cells to lgs')
    parser.add_argument('in_mt', metavar='N', help='in molecular table where alleles are assigned to cells')
    parser.add_argument('read_thresh', metavar='N', help='read threshold')
    parser.add_argument('umi_thresh', metavar='N', help='umi threshold')
    parser.add_argument('cell_thresh', metavar='N', help='cell threshold')
    parser.add_argument('meta_dict_out_fp', metavar='N', help='path to output csv containing lg id and static tag info')
    parser.add_argument('out_fp', metavar='N', help='path to output allele table for lin recon')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.in_mt, parsed_args.read_thresh, parsed_args.umi_thresh, parsed_args.cell_thresh, parsed_args.meta_dict_out_fp, parsed_args.out_fp)
    
    
    
    
    