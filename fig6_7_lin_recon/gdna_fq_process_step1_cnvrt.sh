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
#SBATCH --time=12:00:00

## Set a name for the job, visible in `squeue`
#SBATCH --job-name="10x_te_process_step2"

## The following settings are optimal for *most* software, we want one task 
## to have one or more cores available for that task to fork or use threads.
## One node, -N also works
#SBATCH --nodes=1
## Number of tasks, -n also works. For 10x local mode use only 1 taks per node.
#SBATCH --ntasks=1
## To take advantage of multi-threading, use 16 CPU/core per task, -c also works.
#SBATCH --cpus-per-task=8

## There are to ways to specify memory, --mem= and --mem-per-cpu=
## --mem is usually enough since total job memory is easy to specify 
## this way.
## 256GB of RAM is recommended for 10x runs.
#SBATCH --mem=64G

## Open an job array for multiple 10x Channel
## Always remember to check the number here!!!
## The range of numbers to use for the array, equal to number of 10x channels
#SBATCH --array=1-3

## Specify log file location to help with better logging of errors/outputs.
#SBATCH -o CRcount-%A-%a.out
#SBATCH -e CRcount-%A-%a.err

module add python/3.6.4

SAMPLELIST=./s1_gdna_cnvrt.csv
SEED=$(awk "NR==$SLURM_ARRAY_TASK_ID" $SAMPLELIST)
input_fq=$(echo "$SEED" | cut -d$',' -f1)
out=$(echo "$SEED" | cut -d$',' -f2)

echo $input_fq
echo $out

python3.6 /home/nwhughes/Cassiopeia/python_scripts/pseudo_sc_collapse.py $input_fq $out

