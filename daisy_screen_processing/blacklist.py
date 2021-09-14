import os
#dir = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/all_data_target"
def main():
    
    path = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/blacklist"
    blackList = blacklist(path)
    

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

if __name__ == '__main__':
    main()
