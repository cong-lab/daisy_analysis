import os
import sys
import argparse

def main(Dpath):
    #Dpath = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/all_data_target"    
    path = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/blacklist"
    blackList = blacklist(path)

    for file in os.listdir(Dpath):
        if ".fa" in file:
            current_file = os.path.join(Dpath,file)
            D = open(current_file, 'r')
            list = []
            for l in D:
                list.append(l)
            f = open(file, 'w')
            l = file.split(".")
            BC = l[0]
            counter = 0
            for line in list:
                if counter % 2 == 1:
                    if BC in blackList.keys():
                        if list[counter] not in blackList[BC]:
                            f.write(list[counter - 1])
                            f.write(list[counter])
                    else:
                        f.write(list[counter - 1])
                        f.write(list[counter])
                counter += 1      
        f.close()               
            
        
    

def blacklist(path):
    dic = {}
    for file in os.listdir(path):
            if ".needleall" in file:
                current_file = os.path.join(path,file)
                #print(current_file)
                f = open(current_file, 'r')
                counter = 0
                for line in f:
                    if counter >= 2:
                        #print(line)
                        l = line.split("\t")
                        #print(l[0])
                        if l[0] not in dic.keys():
                            tlist = []
                            if l[9] not in tlist:
                                tlist.append(l[9].strip("\n"))
                            dic[l[0]] = tlist
                        else:
                            if l[9] not in dic[l[0]]:
                                dic[l[0]].append(l[9].strip("\n"))
                    counter += 1
    return dic


def create_arg_parser():
    parser = argparse.ArgumentParser(description='Quantify and rank designs based on CIGAR from bowtie2')
    parser.add_argument('Dpath', metavar='N', help='folder path to bowtie2 sam_out results')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    main(parsed_args.Dpath)
