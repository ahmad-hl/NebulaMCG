import os

currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..', '..','results','EduroamPerf'))
os.chdir(rootDir)
print(os.getcwd())

in_files = [ r'ping4.txt', r'ping3.txt']
with open('wifi_rtt.csv', "w", newline='\n') as rttcsv:
    for infile in in_files:
        # Read vehicles bandwidth --write---> bw.csv
        file = open(infile, "r")
        lines = file.readlines()[1:]

        for line in lines:
            fields = line.split()
            fields_no = len(fields)
            print([fields, fields_no])
            rtt_string = fields[fields_no - 2].replace('time=', '')
            rttcsv.write("{}\n".format(rtt_string))
rttcsv.close()