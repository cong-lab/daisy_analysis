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
#SBATCH --time=24:00:00

## Set a name for the job, visible in `squeue`
#SBATCH --job-name="v2cutmg"

## The following settings are optimal for *most* software, we want one task 
## to have one or more cores available for that task to fork or use threads.
## One node, -N also works
#SBATCH --nodes=1
## Number of tasks, -n also works. For 10x local mode use only 1 taks per node.
#SBATCH --ntasks=1
## To take advantage of multi-threading, use 16 CPU/core per task, -c also works.
#SBATCH --cpus-per-task=4

## There are to ways to specify memory, --mem= and --mem-per-cpu=
## --mem is usually enough since total job memory is easy to specify 
## this way.
## 96GB of RAM is recommended for 10x runs.
#SBATCH --mem=16G

## Open an job array for multiple 10x Channel
## Always remember to check the number here!!!
## The range of numbers to use for the array, equal to number of 10x channels
#SBATCH --array=1-18

## Specify log file location to help with better logging of errors/outputs.
#SBATCH -o cutmg-%A-%a.out
#SBATCH -e cutmg-%A-%a.err

## These are optional, if you want to receive mail about the job.
## Who to send mail to.
##SBATCH --mail-user=congle@stanford.edu
## What type of mail to send
##SBATCH --mail-type=BEGIN,END,FAIL,TIME_LIMIT_80

## Put any module here, anaconda environment example shown here:
## Modules needed for the pipeline to run
module purge
module load anaconda
module load cutadapt/2.3
## Optionally activate environment
## First specify the reference and base path
base_path=/labs/congle/PRT/Hiseq_20190725_TATS
trim_path=/labs/congle/PRT/Hiseq_20190725_TATS/trim_fastqs
## enter base path so make sure 10x sample list is stored here!
cd ${base_path}
mkdir ${trim_path}

## Use bash command to get input sample/channel name, fastqpath, expected cell number from a SAMPLELIST, i.e., 10x sample list
## Sample list should be comma-separated (csv) file that have no header
## Sample list should contain 3 columns for ID, fastq_path(absolute or relative to base_path), expected_cell_number (no comma please) for each channel
SAMPLELIST=./samples.txt
SEED=$(awk "NR==$SLURM_ARRAY_TASK_ID" $SAMPLELIST)
sample_id=$(echo "$SEED" | cut -d$',' -f1)
read1_fq=$(echo "$SEED" | cut -d$',' -f2)
read2_fq=$(echo "$SEED" | cut -d$',' -f3)

echo $sample_id
cd ${trim_path}

srun cutadapt \
	-g CCATCTCATCCCTGCGTGTCTCC \
	-a CATCACCGACTGCCCATAGAGAGG \
	-G CCTCTCTATGGGCAGTCGGTGATG \
	-A GGAGACACGCAGGGATGAGATGG \
	-o "${sample_id}.R1.trimmed.fastq.gz" \
	-p "${sample_id}.R2.trimmed.fastq.gz" \
	-e 0.15 \
	--discard-untrimmed \
	--pair-filter=both \
	-j 0 \
	${read1_fq} \
	${read2_fq}

srun /labs/congle/Software/FLASH2/flash2 \
	-M 300 \
	--allow-outies \
	--compress \
	-o ${sample_id} \
	${sample_id}.R1.trimmed.fastq.gz \
	${sample_id}.R2.trimmed.fastq.gz

## deactivating python virtual environment
# source deactivate

# What variables does SLURM set?
# env | grep SLURM | sort -V

