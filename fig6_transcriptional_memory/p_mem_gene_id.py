import pandas as pd
import itertools
import argparse
from scipy import stats
import sys
import os

def main(countdf, lindistdf, gene_chunk, out_path):
    
    lindist_mat = pd.read_csv(lindistdf, index_col = 0)
    
    count_mat = pd.read_csv(countdf, index_col = 0)
    
    GOI = pd.read_csv(gene_chunk, index_col = 0)
    
    cells = list(count_mat)
    
    cell_combos = list(itertools.combinations(cells, 2))
    
    out_df = pd.DataFrame(index = GOI.index, columns = ["spearman_r", "spearman_p", "pairs_count"])
    
    for gene in GOI.index: # subset the for loop to speed up computation
        
        print("investigating gene: " + gene)
        gene_sries = count_mat.loc[gene]
        combo_df = pd.DataFrame(index = cell_combos)
        
        for cell_combo in cell_combos:
            
            c1 = cell_combo[0]
            
            c2 = cell_combo[1]
            
            exp1 = gene_sries[c1]
            exp2 = gene_sries[c2]
            
            if exp1 != 0 and exp2 != 0: # require gene to be expressed in both cells !
                
                exp_diff = abs(exp1 - exp2)
                
                if c1 in lindist_mat.index and c2 in list(lindist_mat):
                    
                    ldist = lindist_mat.loc[c1, c2]
                    
                    combo_df.loc[cell_combo, "exp_dist"] = exp_diff
                    combo_df.loc[cell_combo, "lin_dist"] = ldist
        
        combo_df_drop = combo_df.dropna(how = "any")
        pairs = len(combo_df_drop)
        
        if pairs >= 3:
        
            spearman = stats.spearmanr(combo_df_drop["exp_dist"], combo_df_drop["lin_dist"])
            pearson = stats.pearsonr(combo_df_drop["exp_dist"], combo_df_drop["lin_dist"])
        
            print("writing gene: " + gene)
            out_df.loc[gene, "spearman_r"] = spearman[0]
            out_df.loc[gene, "spearman_p"] = spearman[1]
            out_df.loc[gene, "pearson_r"] = pearson[0]
            out_df.loc[gene, "pearson_p"] = pearson[1]
            out_df.loc[gene, "pairs_count"] = pairs

    out_df.to_csv(out_path, index_label = "genes")
    
def create_arg_parser():
    parser = argparse.ArgumentParser(description='identify genes with inherited gene expression levels')
    parser.add_argument('countdf', metavar='N', help='folder path to count mat (1)')
    parser.add_argument('lindistdf', metavar='N', help='folder path to lin dist mat (2)')
    parser.add_argument('gene_array', metavar='N', help='list of genes to compute(3)')
    parser.add_argument('out', metavar='N', help='folder path to output (3)')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.countdf, parsed_args.lindistdf, parsed_args.gene_array, parsed_args.out)
    
