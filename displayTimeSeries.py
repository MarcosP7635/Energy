import astropy.units as units
import astropy.constants as constants
import matplotlib.pyplot as plt
import sympy as sym
import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import requests
import re
import subprocess
import urllib.request
from sympy.abc import *
from bs4 import BeautifulSoup
import csv
cwd = subprocess.os.getcwd()

def clean_time_series(time_series):
    '''
    This function takes the time series of power densities and returns a list
    of lists of the time series converted into floats.
    '''
    split_time_series = time_series.replace('[', ' ').replace(']', ' ').replace('\n', ' ').split(' ') 
    return np.round(np.array([float(power_density)  
                    for power_density in split_time_series 
                    if len(power_density)>0]), 2)

time_series_file_path = cwd + '\MeanPowerDensitiesofDecayChains\power_density_time_series.csv'
#read the file to a numpy array
with open(time_series_file_path, newline='\n') as f:
    reader = csv.reader(f)
    time_series_unclean = list(reader)[0]
power_densities_dict = {}
power_densities_dict['Time (seconds)'] = np.logspace(0, 9.5, 10**3)
for row, chain in enumerate(all_decay_chains):
    power_densities_dict[chain.index[0]] = clean_time_series(time_series_unclean[row])
power_densities_df = pd.DataFrame.from_dict(power_densities_dict).set_index(
                        'Time (seconds)')
power_densities_df

#plot multiple scatterplots together with hover names
indices = power_densities_df.index
fig = go.Figure()
for column in power_densities_df.columns:
    if (power_densities_df[column][indices[0]] > 0):
        fig.add_traces(go.Scatter(x = indices, y = power_densities_df[column], 
        mode='markers', name = column)) 
fig.update_xaxes(type = 'log', title = 'Time (seconds)')
fig.update_yaxes(title = 'Power Density (W/g)', type = 'log')
fig.update_layout(title = 'Power Density as a Function of Time')
fig.show()