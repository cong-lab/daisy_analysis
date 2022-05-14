from __future__ import division

import subprocess
import numpy as np
import pandas as pd
import pandascharm as pc
import random
from pylab import *
import pickle as pic
from pathlib import Path

import argparse
from tqdm import tqdm

import Bio.Phylo as Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, ParsimonyScorer, DistanceTreeConstructor
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from skbio import DistanceMatrix
from skbio.tree import nj
from numba import jit
import scipy as sp

import networkx as nx

import sys
import os

from cassiopeia.TreeSolver.lineage_solver import *
from cassiopeia.TreeSolver.simulation_tools import *
from cassiopeia.TreeSolver.utilities import fill_in_tree, tree_collapse
from cassiopeia.TreeSolver import *
from cassiopeia.TreeSolver.Node import Node
from cassiopeia.TreeSolver.Cassiopeia_Tree import Cassiopeia_Tree
import cassiopeia.TreeSolver.data_pipeline as dp
from cassiopeia.TreeSolver.alternative_algorithms import run_nj_weighted, run_nj_naive, run_camin_sokal 

import cassiopeia as sclt

SCLT_PATH = Path(sclt.__path__[0])

def read_mutation_map(mmap):
    """
    Parse file describing the likelihood of state transtions per character.

    Currently, we're just storing the mutation map as a pickle file, so read in with pickle.
    """
    
    mut_map = pic.load(open(mmap, "rb"))

    return mut_map

def main():
    """
    Takes in a character matrix, an algorithm, and an output file and 
    returns a tree in newick format.

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("char_fp", type = str, help="character_matrix")
    parser.add_argument("out_fp", type=str, help="output file name")
    parser.add_argument("-nj", "--neighbor-joining", action="store_true", default=False)
    parser.add_argument("--neighbor_joining_weighted", action='store_true', default=False)
    parser.add_argument("--ilp", action="store_true", default=False)
    parser.add_argument("--hybrid", action="store_true", default=False)
    parser.add_argument("--cutoff", type=int, default=80, help="Cutoff for ILP during Hybrid algorithm")
    parser.add_argument("--time_limit", type=int, default=1500, help="Time limit for ILP convergence")
    parser.add_argument("--greedy", "-g", action="store_true", default=False)
    parser.add_argument("--camin-sokal", "-cs", action="store_true", default=False)
    parser.add_argument("--verbose", action="store_true", default=False, help="output verbosity")
    parser.add_argument("--mutation_map", type=str, default="")
    parser.add_argument("--num_threads", type=int, default=1)
    parser.add_argument("--max_neighborhood_size", type=int, default=10000)
    parser.add_argument("--weighted_ilp", "-w", action='store_true', default=False)
    parser.add_argument("--prune_characters", action='store_true', default=False)

    args = parser.parse_args()

    char_fp = args.char_fp
    out_fp = args.out_fp
    verbose = args.verbose

    cutoff = args.cutoff
    time_limit = args.time_limit
    num_threads = args.num_threads

    max_neighborhood_size = args.max_neighborhood_size

    stem = ''.join(char_fp.split(".")[:-1])

    cm = pd.read_csv(char_fp, sep='\t', index_col=0, dtype=str)

    if args.prune_characters:

        to_drop = []
        for char in cm.columns:

            unique_vals = cm[char].unique()
            if len(unique_vals) == 1:
                to_drop.append(char)
                continue

            #unique_vals = list(map(lambda x: x if x != '-' and x != '0', unique_vals))
            #if len(unique_vals) == 1:
            #    to_drop.append(char)

        cm = cm.drop(columns = to_drop)

    cm_uniq = cm.drop_duplicates(inplace=False)
    #print(cm_uniq)
    
    cm_lookup = list(cm.apply(lambda x: "|".join(x.values), axis=1))
    newick = ""

    prior_probs = None
    if args.mutation_map != "":

        prior_probs = read_mutation_map(args.mutation_map)

    weighted_ilp = args.weighted_ilp
    if prior_probs is None and weighted_ilp:
        raise Exception("If you'd like to use weighted ILP reconstructions, you need to provide a mutation map (i.e. prior probabilities)")

    if args.greedy:

        target_nodes = list(cm_uniq.apply(lambda x: Node(x.name, x.values), axis=1))

        if verbose:
            print('Read in ' + str(cm.shape[0]) + " Cells")
            print('Running Greedy Algorithm on ' + str(len(target_nodes)) + " Unique States")

        reconstructed_network_greedy = solve_lineage_instance(target_nodes, method="greedy", prior_probabilities=prior_probs)
        
        net = reconstructed_network_greedy.get_network()

        root = [n for n in net if net.in_degree(n) == 0][0]
        # score parsimony
        score = 0
        for e in nx.dfs_edges(net, source=root):
            score += e[0].get_mut_length(e[1])
           
        print("Parsimony: " + str(score))

        newick = reconstructed_network_greedy.get_newick()

        with open(out_fp, "w") as f:
            f.write(newick)

        out_stem = "".join(out_fp.split("/")[:-1])
        print("out_fp is: " + out_fp)
        print("out_stem is: " + out_stem)
        pic.dump(reconstructed_network_greedy, open(out_fp + ".pkl", "wb")) 

    elif args.hybrid:

        target_nodes = list(cm_uniq.apply(lambda x: Node(x.name, x.values), axis=1))

        if verbose:
            print('Running Hybrid Algorithm on ' + str(len(target_nodes)) + " Cells")
            print('Parameters: ILP on sets of ' + str(cutoff) + ' cells ' + str(time_limit) + 's to complete optimization') 

        #string_to_sample = dict(zip(target_nodes, cm_uniq.index))

        #target_nodes = list(map(lambda x, n: x + "_" + n, target_nodes, cm_uniq.index))

        print("running algorithm...")
        reconstructed_network_hybrid = solve_lineage_instance(target_nodes, method="hybrid", hybrid_subset_cutoff=cutoff, 
                                                        prior_probabilities=prior_probs, time_limit=time_limit, threads=num_threads, 
                                                        max_neighborhood_size=max_neighborhood_size, weighted_ilp = weighted_ilp)

    
        net = reconstructed_network_hybrid.get_network()
        
        newick = reconstructed_network_hybrid.get_newick()
        #if verbose:
        #    print("Parsimony: " + str(score))
        
        if verbose:
            print("Writing the tree to output...")

        out_stem = "".join(out_fp.split(".")[:-1])
        pic.dump(reconstructed_network_hybrid, open(out_stem + ".pkl", "wb")) 

        with open(out_fp, "w") as f:
            f.write(newick)

        #score parsimony
        score = 0
        for e in net.edges():
          score += e[0].get_mut_length(e[1])
           
        print("Parsimony: " + str(score))


    elif args.ilp:

        target_nodes = list(cm_uniq.apply(lambda x: Node(x.name, x.values), axis=1))

        if verbose:
            print("Running ILP Algorithm on " + str(len(target_nodes)) + " Unique Cells")
            print("Paramters: ILP allowed " + str(time_limit) + "s to complete optimization")

        reconstructed_network_ilp = solve_lineage_instance(target_nodes, method="ilp", prior_probabilities=prior_probs, time_limit=time_limit, 
                                                        max_neighborhood_size=max_neighborhood_size, weighted_ilp = weighted_ilp)

        net = reconstructed_network_ilp.get_network()

        root = [n for n in net if net.in_degree(n) == 0][0]

        # score parsimony
        score = 0
        for e in nx.dfs_edges(net, source=root):
            score += e[0].get_mut_length(e[1])
           
        print("Parsimony: " + str(score))
        
        newick = reconstructed_network_ilp.get_newick()

        if verbose:
            print("Writing the tree to output...")

        out_stem = "".join(out_fp.split(".")[:-1])
        pic.dump(reconstructed_network_ilp, open(out_stem + ".pkl", "wb")) 

        with open(out_fp, "w") as f:
            f.write(newick)


    elif args.neighbor_joining:

        out_stem = "".join(out_fp.split(".")[:-1])

        ret_tree = run_nj_naive(cm_uniq, stem, verbose)

        pic.dump(ret_tree, open(out_stem + ".pkl", "wb")) 

        newick = ret_tree.get_newick()

        with open(out_fp, "w") as f:
           f.write(newick)

       

    elif args.neighbor_joining_weighted:

        out_stem = "".join(out_fp.split(".")[:-1])
        ret_tree = run_nj_weighted(cm_uniq, prior_probs, verbose)

        pic.dump(ret_tree, open(out_fp + ".pkl", "wb"))
        #print("path is : " + str(out_stem))
        
        newick = ret_tree.get_newick()

        with open(out_fp, "w") as f:
            f.write(newick)

    elif args.camin_sokal:
        
        out_stem = "".join(out_fp.split(".")[:-1])

        ret_tree = run_camin_sokal(cm_uniq, stem, verbose)

        pic.dump(ret_tree, open(out_stem + ".pkl", "wb"))

        newick = dp.convert_network_to_newick_format(ret_tree.get_network())
        # newick = ret_tree.get_newick()

        with open(out_fp, "w") as f:
            f.write(newick)
    
    elif alg == "--max-likelihood" or alg == '-ml':

        #cells = cm.index
        #samples = [("s" + str(i)) for i in range(len(cells))]
        #samples_to_cells = dict(zip(samples, cells))
        
        #cm.index = list(range(len(cells)))
        
        if verbose:
            print("Running Maximum Likelihood on " + str(cm.shape[0]) + " Unique Cells")

        infile = stem + 'infile.txt'
        fn = stem + "phylo.txt"
        
        cm.to_csv(fn, sep='\t')

        script = (SCLT_PATH / 'TreeSolver' / 'binarize_multistate_charmat.py')
        cmd =  "python3.6 " + str(script) +  " " + fn + " " + infile + " --relaxed" 
        p = subprocess.Popen(cmd, shell=True)
        pid, ecode = os.waitpid(p.pid, 0)

        os.system("/home/mattjones/software/FastTreeMP < " + infile + " > " + out_fp)
        
        tree = Phylo.parse(out_fp, "newick").next()

        ml_net = Phylo.to_networkx(tree)

        i = 0
        for n in ml_net:
            if n.name is None:
                n.name = "internal" + str(i)
                i += 1

      
        c2str = map(lambda x: str(x), ml_net.nodes())
        c2strdict = dict(zip(ml_net.nodes(), c2str))
        ml_net = nx.relabel_nodes(ml_net, c2strdict)


        out_stem = "".join(out_fp.split(".")[:-1])

        pic.dump(ml_net, open(out_stem + ".pkl", "wb"))

        os.system("rm " + infile)
        os.system("rm " + fn)


    else:
        
        raise Exception("Please choose an algorithm from the list: greedy, hybrid, ilp, nj, max-likelihood, or camin-sokal")

if __name__ == "__main__":
    main()
