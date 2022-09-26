import os

# Unify units into Mb/s
def getBWs_as_Mbits(field):
    components = field.split()
    print(components)
    if field.find("Kbits/sec") > 0:
        return float(components[0]) / 1024
    elif field.find("Gbits/sec") > 0:
        return float(components[0]) * 1024
    elif field.find("Mbits/sec") > 0:
        return float(components[0])
    elif field.find("bits/sec") > 0:
        return float(components[0])

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..', '..','results','EduroamPerf'))
os.chdir(rootDir)
print(os.getcwd())

in_files = ['iperf.txt']
with open('wifi_bw.csv', "w", newline='\n') as bwcsv:
    for infile in in_files:
        # Read vehicles bandwidth --write---> bw.csv
        file = open(infile, "r")
        lines = file.readlines()[6:]

        for line in lines:
            fields = line.split("  ")
            fields_no = len(fields)
            bw_string = fields[fields_no-1].replace('\n', '')
            bw  = getBWs_as_Mbits(bw_string)
            if bw>0:
                bwcsv.write("{}\n".format(bw))
bwcsv.close()





