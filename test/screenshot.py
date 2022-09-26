from mss import mss

sct = mss()
for m in sct.monitors:
    print(m)

print(sct.monitors[1])