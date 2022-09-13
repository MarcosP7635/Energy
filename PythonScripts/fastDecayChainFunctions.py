import astropy.units as units
import astropy.constants as constants
import sympy as sym
import numpy as np 
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import re
import urllib.request
from sympy.abc import *
from bs4 import BeautifulSoup
import csv


def half_life_to_lambda(half_life):
    '''
    This function takes the e-folding times of the entire decay chain.
    Returns the half-life of the nuclide
    '''
    return half_life / np.log(2)


def get_isotope_info(isotope, info = None, isotope_column = None,
    dataset = {}, isotope_list = None, lists_to_search = []):                  
  '''
  isotope_list and list_to_search are optional arguments.
  If list_to_search is not provided, then info must be provided.
  If isotope_list is not provided, then dataset and isotope_column
  must be provided.
  '''
  if isotope_list is None:
    isotope_list = list(dataset[isotope_column])
  row = isotope_list.index(isotope)
  if len(lists_to_search) == 0:
    try:
      lists_to_search = list(dataset[info])
    except:
      print("info to search for not entered")
      return
  try: #only works if there are multiple specified lists to search 
    return [target_list[row] for target_list in lists_to_search]
  except:
    return lists_to_search[row]

def make_decay_chain(isotope, isotope_list, lambda_list, decay_energy_list, daughter_list):
    '''
    This function takes the isotope, e-folding times, and daughter nuclides
    and returns the decay chain.
    '''
    decay_chain = {}
    decay_chain[isotope] = get_isotope_info(isotope, isotope_list = isotope_list, 
        lists_to_search = (lambda_list, decay_energy_list, daughter_list))
    while True:
        isotope = decay_chain[isotope][2]
        try:
            decay_chain[isotope] = get_isotope_info(isotope, isotope_list = isotope_list,
                lists_to_search = (lambda_list, decay_energy_list, daughter_list))
            if(isotope == decay_chain[isotope][2]):
                return decay_chain
        except:
            return pd.DataFrame(decay_chain, index= ("e-Folding Time (seconds)", 
                                "Average beta-decay energy", "Daughter")).transpose()

#Quickly calculating the decay rate of the i-th generation nuclide
def formulate_decay_rate(e_folding_times):
    '''
    The e-folding times must be in a numpy array.
    Returns a formula for the decay rate of each generation. 
    '''
    exponent_array = -1 / e_folding_times
    decay_rates = len(exponent_array)  * [sym.N(0)]
    decay_rates[0] = sym.exp(t * exponent_array[0]) * exponent_array[0]
    for index, L in enumerate(exponent_array[1:]):
        decay_rates[index+1] = decay_rates[index] * (1 + sym.exp(t * L) * L) 
    return decay_rates

def eval_decay_rates(decay_rates, time_array):
    '''
    This function takes the formula for the decay rate of each generation
    and substitutes each value in the time array for t.
    Each decay_rate must be a sympy expression. 
    https://docs.sympy.org/ 
    Rewrite so that the outer loop is over the time array and the inner loop
    is over the generations. This can be done by using (suggested by copilot: 
    the np.meshgrid function) or a 2d array (my first thought)
    '''
    try: #will only evaluate if decay_rates is an array of sympy expressions
        evaluated_decay_rates = [np.array([formula.subs(t, time) for formula in decay_rates])
                                    for time in time_array]
    except:
        evaluated_decay_rates = [decay_rates.subs(t, time) for time in time_array]
    return evaluated_decay_rates


#Calculating the power density of a decay chain
def calc_power_density(decay_rates, decay_energies, initial_mass):
    '''
    Rewrite such that is sums the entire chain and NOT across time
    decay_rates must be a numpy array in moles/second
    decay_energies must be a numpy array in keV/decay
    This function takes the decay rates and energies of the decay chain.
    Returns the power density in watts/g
    '''
    power_density =  [sum(decay_rate_t * decay_energies) for decay_rate_t in decay_rates]
    '''
    At every different value for time, 
    store the sum of the product of each generation's decay rate and decay energy.
    '''
    power_density = np.array(power_density)
    #convert to W/g
    power_density *=  units.keV.to(units.J) * float(constants.N_A * units.mol) / initial_mass
    return np.abs(power_density.astype(float))


def calculate_all_power_densities(all_decay_chains, time_array, mean = True):
    '''
    This function takes the isotope, e-folding times, and daughter nuclides
    and returns power density as a function of time for each decay chain.
    The optional boolean argument mean determines whether the whole time series is returned
    or only its mean. 
    '''
    if mean:
        all_power_densities = [np.mean(calc_power_density(
                                    decay_rates = eval_decay_rates(
                                                    formulate_decay_rate(chain['e-Folding Time (seconds)']), 
                                                    time_array), 
                                    decay_energies = np.array(chain['Average beta-decay energy']),
                                    initial_mass = float(re.sub('\D+', '', chain.index[0]))
                                )) for chain in all_decay_chains]
    else:
        all_power_densities = [calc_power_density(
                                    decay_rates = eval_decay_rates(
                                                    formulate_decay_rate(chain['e-Folding Time (seconds)']), 
                                                    time_array), 
                                    decay_energies = np.array(chain['Average beta-decay energy']),
                                    initial_mass = float(re.sub('\D+', '', chain.index[0]))
                                ) for chain in all_decay_chains]
    return all_power_densities

