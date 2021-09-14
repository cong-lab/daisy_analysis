#!/bin/bash
## No need to change this unless you could also run with a different PI account. 
## Replace MY_PI_SUNetID_or_Project_ID with the PI/project to be charged.
##SBATCH --account=congle

## SCG partitions are batch, interactive and nih_s10
## The batch and nih_s10 partitions require specifying --account=PI_SUNetID where PI_SUNetID is the SUNetID of the PI for the job accounting.
## A --time= time limit must be specified.
## SCG is limited to single node jobs, so most jobs will want --nodes=1 --ntasks=1 --cpus-per-task=N 
## where N is the number of cores for a multithreaded application.
#SBATCH --partition=interactive

## Set job time to 24 hours
#SBATCH --time=48:00:00

## Set a name for the job, visible in `squeue`
#SBATCH --job-name="TATS20190702_2"

## The following settings are optimal for *most* software, we want one task 
## to have one or more cores available for that task to fork or use threads.
## One node, -N also works
#SBATCH --nodes=1
## Number of tasks, -n also works. For 10x local mode use only 1 taks per node.
#SBATCH --ntasks=1
## To take advantage of multi-threading, use 16 CPU/core per task, -c also works.
#SBATCH --cpus-per-task=1

## There are to ways to specify memory, --mem= and --mem-per-cpu=
## --mem is usually enough since total job memory is easy to specify 
## this way.
#SBATCH --mem=32G

## Open an job array for multiple 10x Channel
## Always remember to check the number here!!!
## The range of numbers to use for the array, equal to number of 10x channels
#SBATCH --array=1-18


## Specify log file location to help with better logging of errors/outputs.
#SBATCH -o CRcount-%A-%a.out
#SBATCH -e CRcount-%A-%a.err

## Put any module here, anaconda environment example shown here:
## Modules needed for the pipeline to run
module purge
module load python3

## bcl2fastq only needed for cellranger mkfastq

## Optionally activate environment
#source  activate py3.6

## First specify the reference and base path

base_path=/labs/congle/PRT/Hiseq_20190510_TATS/splitfq_lesscut

## enter base path so make sure 10x sample list is stored here!
#cd ${base_path}

## Use bash command to get input sample/channel name, fastqpath, expected cell number from a SAMPLELIST, i.e., 10x sample list
## Sample list should be comma-separated (csv) file that have no header
## Sample list should contain 3 columns for ID, fastq_path(absolute or relative to base_path), expected_cell_number (no comma please) for each channel

SAMPLELIST=list2.txt
SEED=$(awk "NR==$SLURM_ARRAY_TASK_ID" $SAMPLELIST)
name=$(echo "$SEED" | cut -f 8 -d '/')
#ls $SEED"/"*.fastq > $name".txt"
mkdir $name
cd $name 
python /labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/all_data_target/get_target_2.py $SEED 
#echo $name

# deactivating python virtual environment
# source deactivate

# What variables does SLURM set?
env | grep SLURM | sort -V



