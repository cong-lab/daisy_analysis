import re
import sys
import os


def design_barcode_dictionary(whitelist):
    #whitelist = "/labs/congle/PRT/TATS_v2_indel_analysis/tats_reference/tats_ref.fa"
    wl = open(whitelist, "r")
    counter = 0
    d = {}
    design = ''
    for line in wl:
        #print(line)
        if counter % 2 == 0:
            design = line[1:].rstrip() 
        if counter % 2 == 1:
            m = re.search(r"TTTTTTG[ATGC]{13}", str(line))
            #print(m)
            start = m.start()
            bc = line[start+6:start+20]
            #print(bc)
            d[bc] = design
        counter += 1
    return d

def main():
    whitelist = "/labs/congle/PRT/TATS_v2_indel_analysis/tats_reference/tats_ref.fa"
    #path_o = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/all_data_target/"
    path_o = "/labs/congle/PRT/Hiseq_20190510_TATS/trim_fastqs_lesscut/needleall/filterBeforeDownsample/blacklistPlasmidPool/"
    spl = open("sampleList0715.txt", "r")
    wf = open("list_0715.csv", "w")
    wl = design_barcode_dictionary(whitelist)

    sd = {}
    List = [] 
    for l in wl:
        sd[l] = ''
        List.append(l)


    for j in spl:
        path = path_o + j.rstrip() 
        sp = path.split("/")
        sampleName = sp[len(sp) - 1]
        #sd = {}
        list = []
        for file in os.listdir(path):
            if ".fa" in file:
                current_file = os.path.join(path,file)

                nm = file.split(".")
                name = nm[0]
                design = wl[name]

                list.append(design)
                nb = design.split("_")
                number = int(nb[1])

                f = open(current_file,"r")
                c = 0
                for l in f:
                    c += 1

                sd[name] = sd[name] + str(c/2) + ","
                #print(sd[name])
        for r in wl.keys():
            if wl[r] not in list:
                sd[r] = sd[r] + "0" + ","


    for i in sd:

        print(wl[i] + ","+ i + "," + str(sd[i]))
        wf.write("\n")
        wf.write(wl[i] + ","+ i + "," + str(sd[i]))
    wf.close() 
    
if __name__ == '__main__':
    main()

