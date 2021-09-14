# calculate entropy with bias correction
# filter out efficiency < 0.5

import os
import sys
import math
import argparse

def main(path):
	entropyD = {}
	table = []
	bigD = []
	name1 = ''
	name2 = ''
	for file in os.listdir(path):
		if ".needleall" in file:
			current_file = os.path.join(path,file)
			name1 = current_file.split("/")
			name2 = name1[len(name1)-2]
			sam = open(current_file, 'r')
			count = 0
			d = {}
			unedit_count = 0
			for i in sam:
				count += 1
				design = ""
				if count > 2:
					line = str(i).strip("\n").split("\t")
					cigar = line[5]
					if cigar == "60M":
						unedit_count +=1
					design = line[2]
					if cigar not in d.keys():
						d[cigar] = 1
					else:
						d[cigar] += 1
			if count > 2:
				total_eff = 1 - (unedit_count / (count-2))
			else:
				total_eff = 0
			table.append(design)
			table.append(d)
			bigD.append(table)
			nd = {}
			name = design
			entropy = -1/1000 # bias correction for N = 500
			for j in d.keys():
				nd[j] = d[j]/count
				if nd[j] > 0 and j != 'None':
						entropy += - nd[j]*math.log(nd[j], 2) + 1/1000 # bias correction for N = 500
			if total_eff >= 0.5: 
				entropyD[design] = entropy  # filter design with efficiency < 0.5
	sorted_x = sorted(entropyD.items(), key=lambda kv: kv[1], reverse=True)

	with open(name2 + ".txt", 'w') as f:
		for item in sorted_x:
			#print(item)
			f.write(str(item[0]) + "\t" + str(item[1]))
			f.write("\n")     
 
def create_arg_parse():
	parser = argparse.ArgumentParser()
	parser.add_argument("path", metavar = "path")
	return parser


if __name__ == '__main__':
	arg_parser = create_arg_parse()
	parsed_args = arg_parser.parse_args(sys.argv[1:])
	main(parsed_args.path)       

