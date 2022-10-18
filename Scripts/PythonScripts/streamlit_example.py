import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go

high_res_time_series_df = pd.read_csv(
    "C:\\Users\\engin\\Documents\\Github\\power_densities\\Corrected_power_time_series_201_steps.csv",
    on_bad_lines = 'warn')
high_res_time_series_df.set_index('Parent Isotope', inplace = True)
time_array = [float(t) for t in high_res_time_series_df.columns]
high_res_time_series_df = high_res_time_series_df.transpose()
high_res_time_series_df.columns = [''.join([l for l in isotope if l.isalpha()]) + "-" + 
                                    ''.join([l for l in isotope if l.isdigit()]) 
                                    for isotope in high_res_time_series_df.columns]
entries = [x for x in high_res_time_series_df.columns 
            if np.max(high_res_time_series_df[x]) > 10**-6]
def plot(isotopes):
  fig = go.Figure()
  if len(isotopes) > 1:
    title = "Power Produced by 1 Gram Each of " + ", ".join(isotopes)
  elif len(isotopes) == 1:
    title = "Power Produced by 1 Gram of " + isotopes[0]
  for isotope in isotopes:
    A = int(''.join([l for l in isotope if l.isdigit()]))
    y = high_res_time_series_df[isotope] / A
    fig.add_trace(go.Scatter(x = time_array,
        y = y,
        name = isotope, mode = "markers"))
    y_dict = dict(type = "log", title = "Power (Watts)", nticks = 10,
            range = [-6, np.log10(np.max(y)) + 1])
    x_dict = dict(type = "log", title = "Time (Seconds)", nticks = 12,
                range = [-10, 10])
    fig.update_layout(xaxis = x_dict, yaxis = y_dict,
            title = title)  
  return fig

isotopes = st.multiselect("Select the isotopes to plot", entries)
st.plotly_chart(plot(isotopes), use_container_width=True)

'''
cd .. & cd Energy/Scripts/PythonScripts & conda activate streamlit_env & streamlit run streamlit_example.py
'''
