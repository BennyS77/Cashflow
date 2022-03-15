import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid, JsCode
from myConfig import pageConfig, setSessionData, setSidebar, report_details
from cost_data import getCostSummaryData, getEACdata, processData, calculations
from database_operations import readDatabase, writeToDatabase
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
import numpy as np
import pandas as pd

pageConfig()

report = setSessionData()
st.sidebar.write(f"Company   : {report.company_code}    Job number: {report.job_number}")
st.sidebar.write(f"Start date: {report.start_date.strftime('%d %b %Y')}")
st.sidebar.write(f"Reporting date: {report.reporting_date.strftime('%b %Y')}")
st.sidebar.write(f"End date: {report.end_date.strftime('%d %b %Y')}")


cost_table_name = ('costdata_'+report.company_code+report.job_number).lower()

# baseCostData = processData(report)
# writeToDatabase(baseCostData, cost_table_name)


try:
    baseCostData = readDatabase(cost_table_name)
except:
    st.write(f'Database table: {cost_table_name} does not exist --> import data. ')
    baseCostData = processData(report)
    writeToDatabase(baseCostData, cost_table_name)

tableCostData = calculations(baseCostData, report)
# st.write(tableCostData)

actual_children = configActualChildren(report.start_date, report.reporting_date)
forecast_children = configForecastChildren(report.reporting_date, report.end_date)

gridOptions, custom_css = configureGridOptions(actual_children, forecast_children)

st.markdown("# Cost Forecast")

grid_response = AgGrid(
      dataframe = tableCostData,
      # custom_css = custom_css,
      gridOptions = gridOptions, 
      height = 700,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = 'unique_key',   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=True,  
      data_return_mode='AS_INPUT',
      update_mode='VALUE_CHANGED',   ## default
    #   update_mode='MODEL_CHANGED',
      allow_unsafe_jscode=True
      )
# st.write(actual_children)