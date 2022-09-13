#import the .xls file as a pandas dataframe
import pandas as pd
import numpy as np
import os
import sys
import re
import math
import csv

print(os.getcwd())
file_path = os.getcwd() + "\Radardec4OL.xls"
print(file_path)
df = pd.read_excel(filepath=file_path, sheet_name=None)