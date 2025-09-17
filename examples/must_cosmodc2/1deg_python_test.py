import os
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image
import ceci
import sys
sys.path.insert(0, "/lapp_data/lsst/ebarroso/TXPipe")

my_txpipe_dir = "/lapp_data/lsst/ebarroso/TXPipe"
os.chdir(my_txpipe_dir)

import txpipe
os.makedirs("data/example/outputs_metadetect", exist_ok=True)

