import os
import sys
import argparse
import gzip
#from argparse import ArgumentParser

def main(fn, b, wl):
    #read fastq file and barcode list into a n*5 matrix (faMatrix)#
    # fn = "/labs/congle/PRT/TATS_v2_indel_analysis/fastq_Day0_0510/Rep1_Day0_merged.fq"
    n = 0
    with gzip.open(fn, 'rt') as fh:
        lines = []
        for line in fh:
            lines.append(line.rstrip())
            n = n + 1
#    print(line)
#    print(n)
   
    # b = "/labs/congle/PRT/TATS_v2_indel_analysis/fastq_Day0_0510/barcodes.txt"
    bf = open(b,"r")
    barcode = []
    for l in bf:
        ss = []
        ss.append(l.split(':')[0])
        ss.append(l.split(':')[1][6:16])
        ss.append(l.split(':')[1][6:20])
        barcode.append(ss)   
      
    newfq = []
    for m in barcode:
        newfq.append( lines[int(m[0])-2] )
        newfq.append( lines[int(m[0])-1] )
        newfq.append( lines[int(m[0])] )
        newfq.append( lines[int(m[0])+1] )
        #print(int(m[0])*4)    
    
#    barcode = []
#    bc = "/Users/mac/Downloads/newA.csv"
#    f = open(bc,"r")
#    for item in f:
#        barcode.append(item.rstrip())
    
    fqMatrix = [[0 for x in range(6)] for y in range(len(barcode))]
    for l in range(len(newfq)):
        if l%4 == 0:
            fqMatrix[int(l/4)][0] = newfq[l]
        elif l%4 == 1:
            fqMatrix[int(l/4)][1] = newfq[l]     
        elif l%4 == 2:
            fqMatrix[int(l/4)][2] = newfq[l]
        else:
            fqMatrix[int(l/4)][3] = newfq[l]
        fqMatrix[int(l/4)][4] = barcode[int(l/4)][1]
        fqMatrix[int(l/4)][5] = barcode[int(l/4)][2]
    
    #read white list#
    whiteList = []
    # wl = "/labs/congle/PRT/TATS_v2_indel_analysis/fastq_Day0_0510/ampBC_white_list20190507.csv"
    w = open(wl,'r')
    for wli in w:
        whiteList.append(wli.rstrip())
        
    newList = []
    num = 0
    for ll in range(len(fqMatrix)):
        if fqMatrix[ll][5] in whiteList:
            newList.append(fqMatrix[ll])
    
    keyList = []
    d = {}
    for bm in range(len(newList)):
        if newList[bm][5] not in d.keys():
            a = []
            a.append(newList[bm][0])
            a.append(newList[bm][1])
            a.append(newList[bm][2])
            a.append(newList[bm][3])
            d[newList[bm][5]] = a
        else:
            d[newList[bm][5]].append(newList[bm][0])
            d[newList[bm][5]].append(newList[bm][1])
            d[newList[bm][5]].append(newList[bm][2])
            d[newList[bm][5]].append(newList[bm][3])
            
    for i in d.keys():
        filename = i + ".fastq.gz"
        f = gzip.open(filename, "wt")
        output = '\n'.join(d[i])
        f.write(output)
        f.close()

def create_arg_parser():
    parser = argparse.ArgumentParser(description='Split fastqs by ampliconBC for all designs in whitelist.')
    parser.add_argument('fn', metavar='fq_file', help='full file path to merged sample fastq')
    parser.add_argument('b', metavar='grepbc_file', help='full file path to grepped barcode list')
    parser.add_argument('wl', metavar='whitelist_csv', help='csv file containing barcode whitelist')
    return parser

if __name__ == '__main__':
    arg_parser = create_arg_parser()
    parsed_args = arg_parser.parse_args(sys.argv[1:])
    main(parsed_args.fn, parsed_args.b, parsed_args.wl)

