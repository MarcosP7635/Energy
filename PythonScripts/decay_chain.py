import astropy.units as units
import astropy.constants as constants
import sympy as sym
import numpy as np 
'''
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
'''
import requests
import re
import subprocess
import urllib.request
from sympy.abc import *
# the service URL
livechart = "https://nds.iaea.org/relnsd/v0/data?"
#%matplotlib notebook #incompatible with mpmath
#get the version of python


def lc_read_csv(url):
    '''
    Query the livechart service and return a pandas dataframe. 
    format: lc_read_csv(livechart + "fields=decay_rads&nuclides=" + "16O" + "&rad_types=bm")
    '''
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
    return pd.read_csv(urllib.request.urlopen(req))


def get_daughter_df(parent_df):
    '''
    This function takes a dataframe of parent nuclides and returns a 
    list of dataframes of daughter nuclides
    '''
    daughter_nucleus= [str(int(parent_df['d_z'][row]) + int(parent_df['d_n'][row])) + 
                    ''.join(parent_df['d_symbol'][row]) for row in range(parent_df.shape[0])]
    daughter_df = [lc_read_csv(livechart + "fields=decay_rads&nuclides=" + daughter_nucleus[row].lower() 
                    + "&rad_types=bm") for row in range(parent_df.shape[0])]
    daughter_df = pd.concat(daughter_df)
    return daughter_df
'''
#Testing the functions I copied over from livechart_nuclides.ipynb
df = lc_read_csv(livechart + "fields=decay_rads&nuclides=42ar&rad_types=bm")
daughter_df = get_daughter_df(df)
'''

delta_new, m_0, lambda_m, lambda_d = sym.symbols('\delta_{new} m_0 lambda_m lambda_delta', 
                positive = True, real = True)
delta_tau, tau = sym.symbols('delta_{tau} tau', positive = True, real = True)
lambda_t = sym.symbols('lambda')
#the probability a nucleus with a given e-folding time l after a time t
p = 1 - sym.exp(-1 * tau / lambda_d)
#the daughter nuclei being instantaneously created at a given time t
delta_new = m_0 * sym.exp(-1 * tau / lambda_m) / lambda_m
#daughter nuclei as a function of time
delta_tau = m_0 * (lambda_d * (sym.exp(-1 * tau * (1/lambda_d + 1/lambda_m)) - 1) / (lambda_m + lambda_d) - 
            sym.exp(-1 * tau / lambda_m) + 1)

attempt = sym.integrate(delta_new * p, (tau, 0, t))
eval_attempt = sym.lambdify(([t, lambda_m, lambda_d, m_0]), attempt, 'sympy')
#specify the implementation of the function to be consistent with the input types
#print(eval_attempt(sym.N(0), sym.N(1), sym.N(1), sym.N(1)))

lambda_1, lambda_2, lambda_3, lambda_4, lambda_5 = sym.symbols('lambda_1 lambda_2 lambda_3 lambda_4 lambda_5',
                                                            positive = True, real = True)
l = np.array([lambda_1, lambda_2, lambda_3, lambda_4, lambda_5])
alpha = sym.integrate(np.product([1 - sym.exp(t / (- l_j)) for l_j in l]), (t, 0, tau))
evaluate_alpha = sym.lambdify(([tau]), alpha, 'sympy')
time = np.linspace(0, 5, 100)
abundance = [evaluate_alpha(sym.N(t)).round(6) for t in time] 
abundance.to_csv('abundance.csv')