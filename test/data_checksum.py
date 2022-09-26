import hashlib
import os
import struct

# currDir = os.path.dirname(os.path.realpath(__file__))
# rootDir = os.path.abspath(os.path.join(currDir, '..'))
# LOG_PATH = os.path.join(rootDir, 'client','bw.cl.log')
#
# with open(LOG_PATH, "rb") as f:
#     file_hash = hashlib.md5()
#     chunk = f.read(8192)
#     while chunk:
#         file_hash.update(chunk)
#         chunk = f.read(8192)
#
# print(file_hash.hexdigest())

value=1.234
value2=2.567
value3=3

data = struct.pack('ddi',value,value2,value3)
unpacked_value = struct.unpack('ddi',data)
print(unpacked_value)
print([unpacked_value[0],unpacked_value[1],unpacked_value[2]])
payload_size = struct.calcsize("ddd")
print(payload_size)


from scipy import stats
import numpy as np



test_list = [5.8, 3.4, 3, 3, 3.6]
print(stats.describe(test_list))

test_list = [4, 3.6, 2.7, 2.3, 1.9]
print(stats.describe(test_list))