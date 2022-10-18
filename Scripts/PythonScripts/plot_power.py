import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
'''
Please select the isotope(s) you wish to plot. 
'''
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
        max_y = np.max(high_res_time_series_df[isotopes[0]])
    elif len(isotopes) == 1:
        max_y = np.max(high_res_time_series_df[isotopes[0]])
        title = "Power Produced by 1 Gram of " + isotopes[0]
    for isotope in isotopes:
        A = int(''.join([l for l in isotope if l.isdigit()]))
        y = high_res_time_series_df[isotope] / A
        fig.add_trace(go.Scatter(x = time_array,
            y = y,
            name = isotope, mode = "markers"))
        max_y = max(max_y, np.max(high_res_time_series_df[isotope]))
    if len(isotopes) > 0:
        y_dict = dict(type = "log", title = "Power (Watts)", nticks = 10,
                range = [-6, np.log10(max_y) + 1], showexponent = 'all',exponentformat = 'power' )
        x_dict = dict(type = "log", title = "Time (Seconds)", nticks = 10,
                    range = [-10, 10], showexponent = 'all',exponentformat = 'power')
        fig.update_layout(xaxis = x_dict, yaxis = y_dict, title = title, legend_title="Legend", 
            font=dict(family="Arial, monospace", size=16, color="White"))
    return fig

isotopes = st.multiselect("Select here", entries)
st.plotly_chart(plot(isotopes))#, use_container_width=True)

