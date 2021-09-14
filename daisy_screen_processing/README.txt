#run the sample list generation script by:
./generate_sample_file_Fq_csv.sh Fastq/ > samples.txt

#then double check cl_tats_cutmerge_pe.sh to make sure all variable/path are correct
#then run the cutmerge script to cut adapter and merge R1,R2 fastq by:
sbatch cl_tats_cutmerge_pe.sh

#after this step, could merge with non-default alternative setting with FLASH by:
sbatch cl_tats_pe_merge8.sh

#when merge is finalized, generate merged fastq file list by:
./generate_list_mergedfq_csv.sh {output_folder_from_previous_step} > mergefq_list.txt

#then generate barcode list via grepping for the barcode pattern
#pattern is specified in the file: grep_command.txt, for one file or small list directly grep
#or run parallel grepping BC region on folder containing merged fastq submit srun by:
srun --partition=interactive --mem=64G --time=2:00:00 ./grep_bc_region.sh ./trim_fastqs

#then split fastq via their amplicon BC into individual fqs of all designs.
#make sure to check all path and file name within cl_tats_splitfq.sh before running!
#make sure to use the correct array number equal to the line number of merged fq list:
cat mergefq_list.txt | wc -l
sbatch cl_tats_splitfq_gz.sh

#after split we could now make alignment of target sample
#we first generate csv file containing all fastq list by:
cp generate_designfq_list.sh {master_folder_for_all_samples}
srun --partition=interactive --mem=32G --time=1:00:00 ./generate_designfq_list.sh .
#this way you should have a list of csv each containing fq file list for that sample

#make sure the run_path and array number is adjusted based on line number of csv

#then enter run folder and submit job

#now to summarize preliminary resuls via diversity of CIGAR string in sam file
#first, make sure to copy nessary scripts into the subfolder for the samples by:

#then, generate list of sam_out folder with sample_id by:

#check all parameters like array number and change base_path for submission:

#finally run the script for all folders within the base_path by:





