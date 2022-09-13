'''
Following the instructions from 
https://biach1312.medium.com/how-to-create-a-data-driven-web-application-in-python-99d3c55fdf59
https://www.streamlit.io for more information and API documentation
'''
import streamlit as st
import pandas as pd
import numpy as np
import itertools as IT
import altair as alt
from PIL import Image

st.title("Interactive Data Driven Dashboard")

#Load Data function
@st.cache
def load_data(nrows):
    data = pd.read_csv('C:/Users/engin/Documents/GitHub/Computing-and-Formatting/amazonData/amazon-final.csv',
                        delimiter = ';')
    data['date first available'] = pd.to_datetime(data['date first available'])
    data = data.sort_values(by=['date first available'])
    data = data.set_index(data['date first available'])
    data['discount percentage'] = (data['discount percentage'].str.replace("%",'')). astype(int) 
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    return data

# Loading data text...
data_load_state = st.text('Loading data...')
# Load 1000 rows of data
data = load_data(1000)
# Successfull data loaded
data_load_state.text("Done! (using st.cache)")

#show whole dataset
if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

#show seller and products based on the select filter 
sellers = data[['seller name', 'product name']]
options = st.multiselect("Select seller name to show corresponding sold products: ",sellers['seller name'].unique())
st.write(options)
show = sellers['seller name'].isin(options)
data_seller = sellers[show]
st.write(data_seller)

#Show mrp, discount % and sale price based on the selected year filter in the bar graph

discounts = data[['mrp','discount percentage', 'sale price']]

year_to_filter = st.slider('date', 2014, 2020, 2017)  # min: 2015, max: 2020, default: 2017
filtered_data = discounts[data['date first available'].dt.year == year_to_filter]

st.bar_chart(filtered_data)