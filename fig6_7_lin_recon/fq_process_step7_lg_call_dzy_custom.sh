#!/bin/bash
## Replace MY_PI_SUNetID_or_Project_ID with the PI/project to be charged.
#SBATCH --account=congle

## SCG partitions are batch, interactive and nih_s10
## The batch and nih_s10 partitions require specifying --account=PI_SUNetID where PI_SUNetID is the SUNetID of the PI for the job accounting.
## A --time= time limit must be specified.
## SCG is limited to single node jobs, so most jobs will want --nodes=1 --ntasks=1 --cpus-per-task=N 
## where N is the number of cores for a multithreaded application.
#SBATCH --partition=batch

## Set job time to 24 hours
#SBATCH --time=24:00:00

## Set a name for the job, visible in `squeue`
#SBATCH --job-name="10x_te_process_step2"

## The following settings are optimal for *most* software, we want one task 
## to have one or more cores available for that task to fork or use threads.
## One node, -N also works
#SBATCH --nodes=1
## Number of tasks, -n also works. For 10x local mode use only 1 taks per node.
#SBATCH --ntasks=1
## To take advantage of multi-threading, use 16 CPU/core per task, -c also works.
#SBATCH --cpus-per-task=16

## There are to ways to specify memory, --mem= and --mem-per-cpu=
## --mem is usually enough since total job memory is easy to specify 
## this way.
## 256GB of RAM is recommended for 10x runs.
#SBATCH --mem=128G

## Open an job array for multiple 10x Channel
## Always remember to check the number here!!!
## The range of numbers to use for the array, equal to number of 10x channels
#SBATCH --array=17-28

module add python/3.6.4
module add samtools

SAMPLELIST=./step7_lg_call_dzy.txt
SEED=$(awk "NR==$SLURM_ARRAY_TASK_ID" $SAMPLELIST)
in_mt=$(echo "$SEED" | cut -d$',' -f1)
read_thresh=$(echo "$SEED" | cut -d$',' -f2)
umi_thresh=$(echo "$SEED" | cut -d$',' -f3)
cell_thresh=$(echo "$SEED" | cut -d$',' -f4)
meta_out_fp=$(echo "$SEED" | cut -d$',' -f5)
out_fp=$(echo "$SEED" | cut -d$',' -f6)


python3.6 ./dzy_4t_lg_group.py $in_mt $read_thresh $umi_thresh $cell_thresh $meta_out_fp $out_fp

