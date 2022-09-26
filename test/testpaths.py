import os

currDir = os.path.dirname(os.path.realpath(__file__))
Log_PATH = os.path.join(currDir, '..', 'inout_data')
print([os.path.abspath(currDir), Log_PATH])