import pyshark

capture = pyshark.FileCapture('/home/symlab/ahmad/varbw20ms1plr.pcap', display_filter='tcp.analysis.fast_retransmission or tcp.analysis.retransmission')
counter = 0
for packet in capture:
  counter +=1

print (f'Retransmission packet: {counter}')