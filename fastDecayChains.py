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
cwd = subprocess.os.getcwd()

from fastDecayChainFunctions import *

try: 
    nuclide_df = pd.read_csv(cwd + '\\NuclideData.csv').iloc[:,1:]
except:
    nuclide_df = pd.read_csv(cwd + '/NuclideData.csv').iloc[:,1:]
half_lives = nuclide_df['Half life (years)'].to_numpy() 
nuclide_df["e Folding Time (seconds)"] = half_life_to_lambda(half_lives * units.year.to(units.s))

element_symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 
'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 
'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 
'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 
'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 
'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 
'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm',
 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 
 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 
 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 
 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt',
  'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og', 'N/A']
len(element_symbols)
#to find the daughter nuclide we only need to increment by 1 in the element symbols.
element_symbols[element_symbols.index('Ni')+1]
#remove numbers from string
s = element_symbols
nuclide_df['Daugher Nucleus'] = [re.sub('\D+', '', n) + s[s.index(re.sub('\d+', '', n))+1] 
if re.sub('\d+', '', n) in s else 'N/A' for n in nuclide_df['Isotope'] ]

isotope_list = list(nuclide_df['Isotope'])
lambda_list = list(nuclide_df['e Folding Time (seconds)'])
decay_energy_list = list(nuclide_df['Average beta decay energy'])
daughter_list = list(nuclide_df['Daugher Nucleus'])

all_decay_chains = [make_decay_chain(isotope, isotope_list, lambda_list, decay_energy_list, daughter_list) 
                    for isotope in isotope_list]
time_array = np.logspace(1, 9.5, 10)

mean_power_densities = calculate_all_power_densities(all_decay_chains[:2], time_array, mean = True)
