import subprocess, time

password= ''
command = ' iftop -s 1 -t -i eno1'

proc = subprocess.Popen('sudo -S'+command,shell=True,  stdin=None, stderr=None, stdout=subprocess.PIPE)
output = proc.communicate(password.encode())
time.sleep(1.1)
print(output)




