#!/bin/bash
## No need to change this unless you could also run with a different PI account. 
## Replace MY_PI_SUNetID_or_Project_ID with the PI/project to be charged.
##SBATCH --account=congle

## SCG partitions are batch, interactive and nih_s10
## The batch and nih_s10 partitions require specifying --account=PI_SUNetID where PI_SUNetID is the SUNetID of the PI for the job accounting.
## SCG is limited to single node jobs, so most jobs will want --nodes=1 --ntasks=1 --cpus-per-task=N 
#SBATCH --partition=interactive

## Set job time to 24 hours
#SBATCH --time=48:00:00

## Set a name for the job, visible in `squeue`
#SBATCH --job-name="splitgz"

## The following settings are optimal for *most* software, we want one task 
## One node, -N also works
#SBATCH --nodes=1
## Number of tasks, -n also works. For 10x local mode use only 1 taks per node.
#SBATCH --ntasks=1
## To take advantage of multi-threading, use 16 CPU/core per task, -c also works.
#SBATCH --cpus-per-task=1

## There are to ways to specify memory, --mem= and --mem-per-cpu=
## 16GB should be sufficient usually, 96GB RAM is recommended for large runs.
#SBATCH --mem=32G

## Open an job array for multiple 10x Channel
## Always remember to check the number here!!!
## The range of numbers to use for the array, equal to number of 10x channels
#SBATCH --array=1-18

## Specify log file location to help with better logging of errors/outputs.
#SBATCH -o TATSsplitgz-%A.out
#SBATCH -e TATSsplitgz-%A.err

## These are optional, if you want to receive mail about the job.
## Who to send mail to.
##SBATCH --mail-user=congle@stanford.edu
## What type of mail to send
##SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80

## Put any module here, anaconda environment example shown here:
## Modules needed for the pipeline to run
module purge
module load anaconda
# module load bcl2fastq2/2.20.0
## Optionally activate environment
# source  activate py3.6

## Can alter this to do whatever you please
## First specify the reference and base path
base_path=/labs/congle/PRT/Hiseq_20190725_TATS
splitfq_path=/labs/congle/PRT/Hiseq_20190725_TATS/splitfq_gz
## Specify the path to grepped bc list
bc_grep_path=/labs/congle/PRT/Hiseq_20190725_TATS/bc_grep_list
## Specify input file or constant or value
whitelist_file=/labs/congle/PRT/Hiseq_20190510_TATS/ampBC_white_list20190507.csv

## enter base path so make sure 10x sample list is stored here!
cd ${base_path}
mkdir ${splitfq_path}

## Sample list should be comma-separated (csv) file that have no header
## Sample list should contain 2 columns for ID, fastq_path(absolute or relative to base_path)
SAMPLELIST=./mergefq_list.txt
SEED=$(awk "NR==$SLURM_ARRAY_TASK_ID" $SAMPLELIST)

sample_id=$(echo "$SEED" | cut -d$',' -f1)
merged_fq=$(echo "$SEED" | cut -d$',' -f2)

echo $sample_id
echo $merged_fq
# make directory for each sample within splitfq_path
mkdir ${splitfq_path}"/"${sample_id}
cd ${splitfq_path}"/"${sample_id}

python ${base_path}"/"fqsplit_gz.py \
	"${merged_fq}" \
	"${bc_grep_path}/${sample_id}.bcgrep.txt" \
	"${whitelist_file}"

## deactivating python virtual environment
# source deactivate

# What variables does SLURM set?
# env | grep SLURM | sort -V

