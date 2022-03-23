from queue import Empty
import streamlit as st
import pandas as pd
from my_config import pageConfig, setSessionData
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cost_data import createForecastDetails

pageConfig()

if 'table_1' not in st.session_state:
    st.session_state.table_1 = []
if 'table_1_exists' not in st.session_state:
    st.session_state.table_1_exists = False


company = 'G01'
job = 'PD140479'
# item_list = ['DV01','DV02']
item_list = {'CostItem':['DV01','DV02']}
date_range = pd.date_range(start=datetime(2021,1,1), end=datetime.today(), freq='M').tolist()

forecast_end_date = st.sidebar.date_input("forecast end date")
reporting_month = st.sidebar.selectbox("Reporting month:", date_range, format_func=lambda x: x.strftime('%b %Y'), key="reportingmonth")

if st.session_state.table_1_exists == False:
    st.write("Table does not exist in database - need to create")
    st.session_state.table_1 = createForecastDetails(item_list, reporting_month, forecast_end_date)
    st.session_state.table_1_exists = True

st.write("The data in the 'database'")
st.write(st.session_state.table_1)

if st.session_state.table_1_exists == True:
    data_for_reporting_month = st.session_state.table_1.loc[st.session_state.table_1['reporting_month'] == reporting_month]
    

if len(data_for_reporting_month) > 0:
    st.write("Data for the reporting month already exists")
    st.write(data_for_reporting_month)
    if data_for_reporting_month['forecast_end_date'].iloc[0] < forecast_end_date:
        st.write("forecast end date is different.")
        append_table = createForecastDetails({'CostItem':['test']}, reporting_month, forecast_end_date)
        data_for_reporting_month = data_for_reporting_month.append(append_table)
        data_for_reporting_month = data_for_reporting_month[data_for_reporting_month.CostItem != 'test']
    if data_for_reporting_month['forecast_end_date'].iloc[0] > forecast_end_date:
        st.write("try 'append' with options to reduce number of columns???? ")
    st.write(data_for_reporting_month)
else:
    st.write("No data for reporting month - need to create ")
    table_2 = createForecastDetails(item_list, reporting_month, forecast_end_date)
    st.write(table_2)
    st.session_state.table_1 = st.session_state.table_1.append(table_2)

st.write("The data now in the 'database'")
st.write(st.session_state.table_1)

def on_button_click():
    st.session_state.table_1['Oct 21'] = st.session_state.table_1.apply(lambda x: 55 if x.reporting_month == reporting_month.date() else x['Oct 21'], axis=1)

st.sidebar.button("update data:", on_click = on_button_click)
