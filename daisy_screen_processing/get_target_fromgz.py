import re
import sys
import os
import argparse
import gzip
#dir = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/oligo_pool/20190620_plasmid_pool.extendedFrags.fastq"
#d = open(dir, "r")

#dirList = dir.split('/')
#name = dirList[len(dirList) - 1]
#path = "/labs/congle/PRT/Hiseq_20190510_TATS/splitfq_lesscut/test"

def main(path):

    for file in os.listdir(path):
        if ".fastq.gz" in file:
            current_file = os.path.join(path, file)
            data = gzip.open(current_file, "rb")
            dataList = file.split('.')
            pre = dataList[0]
            print(pre)
            #name = pre + "_t.fastq"
            f = open(pre + ".fa", "w")
            counter = 0
            with open(current_file) as fq:
                for line in fq:
                    print(counter)
                    print(line)
                    if counter % 4 == 0:
                        f.write(">"+pre)
                        f.write("\n")
                    if counter % 4 == 1:
                                      
                        m = re.search(pre, str(line))
                  
                        start = m.start()
                        subline = line[start:(len(line) - 1)]
                        target = subline[0:-42]
                        if len(target) != 0 or start == None:
                            f.write(target)
                            f.write("\n")
                           
                        else:
                            f.write(pre)
                            f.write("\n")
                            
                    
                    counter += 1
                f.close()
        
def create_arg_parser():
    parser = argparse.ArgumentParser(description='Quantify and rank designs based on CIGAR from bowtie2')
    parser.add_argument('path', metavar='N', help='folder path to bowtie2 sam_out results')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    main(parsed_args.path)
