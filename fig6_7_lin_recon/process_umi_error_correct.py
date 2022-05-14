# copy specific chunks of code needed for this step

import sys
import os
import pandas as pd 
import numpy as np
import tqdm
from pathlib import Path
import bokeh.palettes
import time
import matplotlib.pyplot as plt
import subprocess
import argparse
import pysam
import heapq
import yaml


from hits import fastq, utilities, sw, sam
from hits import annotation as annotation_module

from collapse_cython import hq_mismatches_from_seed, hq_hamming_distance, hamming_distance_matrix, register_corrections

progress = tqdm.tqdm

CELL_BC_TAG = 'CB'
UMI_TAG = 'UR'
NUM_READS_TAG = 'ZR'
CLUSTER_ID_TAG = 'ZC'
LOC_TAG = "BC"
CO_TAG = "CO"

HIGH_Q = 31
LOW_Q = 10
N_Q = 2

SCLT_PATH = "/home/nwhughes/Cassiopeia/cassiopeia"

cell_key = lambda al: al.get_tag(CELL_BC_TAG)
UMI_key = lambda al: al.get_tag(UMI_TAG)
loc_key = lambda al: (al.get_tag(LOC_TAG))
empty_header = pysam.AlignmentHeader()

def sort_cellranger_bam(bam_fn, sorted_fn, sort_key, filter_func, show_progress=False):
    Path(sorted_fn).parent.mkdir(exist_ok=True)

    bam_fh = pysam.AlignmentFile(str(bam_fn))

    als = bam_fh

    relevant = filter(filter_func, als)

    max_read_length = 0
    total_reads_out = 0
    
    chunk_fns = []
        
    for i, chunk in enumerate(utilities.chunks(relevant, 10000000)):
        suffix = '.{:06d}.bam'.format(i)
        chunk_fn = Path(sorted_fn).with_suffix(suffix)
        sorted_chunk = sorted(chunk, key=sort_key)
    
        with pysam.AlignmentFile(str(chunk_fn), 'wb', template=bam_fh) as fh:
            for al in sorted_chunk:
                max_read_length = max(max_read_length, al.query_length)
                total_reads_out += 1
                fh.write(al)

        chunk_fns.append(chunk_fn)

    chunk_fhs = [pysam.AlignmentFile(str(fn), check_header=False, check_sq=False) for fn in chunk_fns]

    with pysam.AlignmentFile(str(sorted_fn), 'wb', template=bam_fh) as fh:
        merged_chunks = heapq.merge(*chunk_fhs, key=sort_key)

        if show_progress:
            merged_chunks = progress(merged_chunks, total=total_reads_out, desc='Merging sorted chunks')

        for al in merged_chunks:
            fh.write(al)

    for fh in chunk_fhs:
        fh.close()

  #  for fn in chunk_fns:
  #      fn.unlink()
    
    yaml_fn = Path(sorted_fn).with_suffix('.yaml')
    stats = {
        'total_reads': total_reads_out,
        'max_read_length': max_read_length,
    }

    with open(yaml_fn, "w") as f:
        f.write(yaml.dump(stats, default_flow_style=False))
    #yaml_fn.write_text(yaml.dump(stats, default_flow_style=False))
    
def error_correct_UMIs(cell_group, sampleID, max_UMI_distance): # why does this equal 1 when I am passing in 2?
    
    UMIs = [al.get_tag(UMI_TAG) for al in cell_group]
    print("###########finding UMIs#########")
    print(UMIs)
    ds = hamming_distance_matrix(UMIs)

    corrections = register_corrections(ds, max_UMI_distance, UMIs)
    print("########correcting UMIs#######")
    print(corrections)
    num_corrections = 0
    corrected_group = []
    ec_string = ""
    total = 0;
    corrected_names = []
    for al in cell_group:
        al_umi = al.get_tag(UMI_TAG)
        for al2 in cell_group:
            al2_umi = al2.get_tag(UMI_TAG)
            # correction keys are 'from' and values are 'to'
            # so correct al2 to al
            if al2_umi in corrections.keys() and corrections[al2_umi] == al_umi:

                bad_qname = al2.query_name
                bad_nr = bad_qname.split("_")[-1]
                qname = al.query_name
                split_qname = qname.split("_")

                prev_nr = split_qname[-1]

                split_qname[-1] = str(int(split_qname[-1]) + int(bad_nr))
                n_qname = '_'.join(split_qname)


                al.query_name = n_qname

                ec_string += al2.get_tag(UMI_TAG) + "\t" + al.get_tag(UMI_TAG) + "\t" + al.get_tag(LOC_TAG) + "\t" + al.get_tag(CO_TAG) + "\t" + str(bad_nr) + "\t" + str(prev_nr) + "\t" + str(split_qname[-1]) + "\t" + sampleID + "\n"


                # update alignment if already seen
                if al.get_tag(UMI_TAG) in list(map(lambda x: x.get_tag(UMI_TAG), corrected_group)):
                    corrected_group.remove(al)

                corrected_group.append(al)

                num_corrections += 1
                corrected_names.append(al2.get_tag(UMI_TAG))
                corrected_names.append(al.get_tag(UMI_TAG))
                print("number of corrections: " + str(num_corrections))
    print("#########corrected names list is: ########")
    print(corrected_names)
    
    print("########corrected group is: ########")
    print(corrected_group)
    return corrected_group
    
def error_correct_allUMIs(sorted_fn,
                            max_UMI_distance,
                            sampleID,
                            log_fh = None, 
                            show_progress=True):

    collapsed_fn = sorted_fn.with_name(sorted_fn.stem + '_ec.bam') # this file is empty
    log_fn = sorted_fn.with_name(sorted_fn.stem + '_umi_ec_log.txt')
    
    sorted_als = pysam.AlignmentFile(str(sorted_fn), check_sq=False)

    # group_by only works if sorted_als is already sorted by loc_key
    allele_groups = utilities.group_by(sorted_als, loc_key) # this is where you are having a problem
    num_corrected = 0 # I'm worried that this should actially be num_corr and total should be tot -- there is an error below
    total = 0
    
    with pysam.AlignmentFile(str(collapsed_fn), 'wb', header=sorted_als.header) as collapsed_fh:
        for allele_bc, allele_group in allele_groups:
            if max_UMI_distance > 0:
                print("passing the following group to error_correct_UMIS function: ")
                print(allele_bc)
                print(allele_group)
                #allele_group, num_corr, tot, erstring = error_correct_UMIs(allele_group, sampleID,  max_UMI_distance)
                correction = error_correct_UMIs(allele_group, sampleID,  max_UMI_distance)
                for a in correction:
                    collapsed_fh.write(a)
                
            #print("#####after passing to other function, allele group is: ######")
            #print(allele_group)
            #for a in allele_group:
            #    collapsed_fh.write(a)

            #log_fh.write(error_corrections)
            #if log_fh is None:
            #    print(erstring, end=' ')
            #    sys.stdout.flush()
            #else:
            #    with open(log_fh, "a") as f:
             #       f.write(erstring)

            #num_corrected += num_corr
            #total += tot

    #print(str(num_corrected) + " UMIs Corrected of " + str(total) + " (" + str(round( float(num_corrected) / total, 5)*100) + "%)", file=sys.stderr)
    
def convert_bam_to_moleculeTable(bam_input, mt_out):
    """
    Converts a BAM file to a molecule table Dataframe.

    :param bam_input:
        BAM input file 
    :param mt_out:
        File path to write the molecule table.
    :return:
        None.
    """

    perl_script = (SCLT_PATH + "/ProcessingPipeline/process/processBam2MT_tats.pl")
    cmd = "perl " + str(perl_script) + " " + str(bam_input) + " " + str(mt_out) 

    p = subprocess.Popen(cmd, shell=True)
    pid, ecode = os.waitpid(p.pid, 0)


def main(input_fn, _id, log_file, max_UMI_distance=2, show_progress=True):
    """
    Error correct UMIs together within equivalence classes, as defined as the same cellBC-intBC pair. UMIs whose identifier 
    is within the maximum UMI distance are corrected towards whichever UMI is more abundant. 

    :param input_fn:
        Input file name.
    :param _id:
        Identification of sample.
    :param log_file:
        Filepath for logging error correction information.
    :param max_UMI_distance:
        Maximum UMI distance allowed for error correction.
    :param show_progress:
        Allow a progress bar to be shown.
    :return:
        None; a table of error corrected UMIs is written to file.

    """

    sort_key = lambda al: (al.get_tag(LOC_TAG), -1*int(al.query_name.split("_")[-1]))
    #print("sort key is: " + str(sort_key))
    
    name = Path(input_fn)
    sorted_fn = name.with_name(name.stem + "_sorted.bam")

    filter_func = lambda al: al.has_tag(LOC_TAG) or al.has_tag(CELL_BC_TAG)

    sort_cellranger_bam(input_fn, sorted_fn, sort_key, filter_func, show_progress = show_progress)

    error_correct_allUMIs(sorted_fn, 
                              max_UMI_distance,
                              _id, 
                              log_fh = log_file,
                            show_progress = show_progress)

    ec_fh = sorted_fn.with_name(sorted_fn.stem + "_ec.bam")
    mt_fh = Path(str(ec_fh).split(".")[0] + ".moleculeTable.txt")

    convert_bam_to_moleculeTable(ec_fh, mt_fh)

def create_arg_parser():
    parser = argparse.ArgumentParser(description='binarize states encoded by cpf1-induced indels')
    parser.add_argument('in_bam', metavar='N', help='input bam containing indel calls (1)')
    parser.add_argument('task_id', metavar='N', help='task id for umi correction (2)')
    parser.add_argument('out_log', metavar='N', help='log file (3)')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    print(parsed_args)
    read_in = main(parsed_args.in_bam, parsed_args.task_id, parsed_args.out_log)
    



