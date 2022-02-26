import streamlit as st
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode
import plotly.express as px
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js, percent_formatter, cellStyle_test

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="collapsed"  #expanded" #"collapsed" #auto
)

if 'check' not in st.session_state:
  st.session_state.check = 0

st.session_state.check = st.session_state.check + 1
# st.write("session state check:", st.session_state.check)


## session state to only contain non-calculated values and parameters
## is the values/parameters needed to calculated for forecasts.
## forecastMethod and monthly percentages (everything will be based on percentages, at least initially)
## This first dataframe is what will be loaded in from raw data when project started.
## REPEAT:   NON-CALCULATED values only!!
if 'grid_data' not in st.session_state:
  st.session_state.grid_data = pd.DataFrame.from_dict(
                                  {
                                    "costItem":['110','140','210'],
                                    "EAC":[1000.678,3000,2400.3],
                                    "ACTD":[600,800.555,222.2],
                                    "actual_$":[600,800.555,222.2],
                                    "forecastMethod":['Timeline','Timeline','Timeline'],
                                    "Month_0_percent":[20,20,20],
                                    "Month_1_percent":[60,60,60],
                                    "Month_2_percent":[100,100,100]
                                  }
  )

if 'actualMonths' not in st.session_state:
  st.session_state.actualMonths = 3
if 'forecastMonths' not in st.session_state:
  st.session_state.forecastMonths = 3
if 'numOfDays' not in st.session_state:
  st.session_state.numOfDays = 45
if 'workDaysInMonth' not in st.session_state:
  st.session_state.workDaysInMonth = 25


grid_data = st.session_state.grid_data

def calcs():
  grid_data['ETC'] = grid_data.EAC - grid_data.ACTD
  grid_data['numDays'] = st.session_state.numOfDays
  grid_data['showDays'] = st.session_state.numOfDays
  grid_data['actual_percent'] = grid_data['actual_$'] / grid_data['EAC'] * 100


# percentSoFar = grid_data['actual_percent'] / 100
#   dollarsPerDay = grid_data['ETC'] / grid_data['numDays']
#   workDaysLeft = st.session_state.numOfDays
#   for i in range(st.session_state.forecastMonths):
#     for j in range(len(grid_data)):
#         if workDaysLeft >= st.session_state.workDaysInMonth and grid_data['forecastMethod'].iloc[j]=='Timeline':
#           grid_data['Month_'+str(i)+'_$'] = st.session_state.workDaysInMonth*dollarsPerDay
#           grid_data['Month_'+str(i)+'_percent'] = (percentSoFar + (grid_data['Month_'+str(i)+'_$'] / grid_data['EAC']))*100
#           percentSoFar = percentSoFar + (grid_data['Month_'+str(i)+'_$'] / grid_data['EAC'])
#         elif workDaysLeft > 0:
#           grid_data['Month_'+str(i)+'_$'] = workDaysLeft*dollarsPerDay
#           grid_data['Month_'+str(i)+'_percent'] = (percentSoFar + (grid_data['Month_'+str(i)+'_$'] / grid_data['EAC']))*100
#           percentSoFar = percentSoFar + (grid_data['Month_'+str(i)+'_$'] / grid_data['EAC'])
#         else:
#           grid_data['Month_'+str(i)+'_$'] = 0
#           grid_data['Month_'+str(i)+'_percent'] = 0
#     workDaysLeft = workDaysLeft - st.session_state.workDaysInMonth



calcs()

st.session_state.grid_data = grid_data

dateIsEditable = True
percentIsEditable = True

gridOptions={
  "defaultColDef": {
    "minWidth": 50,
    "maxWidth": 95,
    "filter": True,
    "resizable": True,
    "sortable": True
  },
  "columnDefs": [
    { "headerName": "Cost Item",
      "field": "costItem",
      "maxWidth": 95,
      # "hide": True,
    },
    { "headerName": "EAC",
      "field": "EAC",
      "editable": True,
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "ACTD",
      "field": "ACTD",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "ETC",
      "field": "ETC",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Forecast Method",
      "field": "forecastMethod",
      "editable": True,
      "cellStyle": cellStyle_test,
      "cellEditor": 'agRichSelectCellEditor',
      "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
    },
    { "headerName": "Days",
      "field": "numDays",
      "editable": True,
      "maxWidth": 75,
      "hide":True,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
    },
    { "headerName": "showDays",
      "field": "showDays",
      "editable": True,
      "maxWidth": 75,
      "cellStyle": cellStyle_test,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      # "valueFormatter":"data.numDays"
    },
    { "headerName": "Actual %",
      "field": "actual_percent",
      "editable": True,
      "maxWidth": 75,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    },
    { "headerName": "Actual $",
      "field": "actual_$",
      "maxWidth": 75,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Mth_0_%",
      "field": "Month_0_percent",
      "editable": percentIsEditable,
      "cellStyle": cellStyle_test,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    },
    { "headerName": "Mth_0_$",
      # "field": "Month_0_$",
      "editable": True,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueGetter": "parseFloat((data.Month_0_percent - data.actual_percent)/100 * data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Mth_1_%",
      "field": "Month_1_percent",
      "editable": percentIsEditable,
      "cellStyle": cellStyle_test,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    },
    { "headerName": "Mth_1_$",
      # "field": "Month_1_$",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueGetter": "parseFloat((data.Month_1_percent - data.Month_0_percent)/100 * data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      # "valueFormatter": "parseFloat((data.Month_1_percent - data.Month_0_percent)/100 * data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Mth_2_%",
      "field": "Month_2_percent",
      "editable": percentIsEditable,
      "cellStyle": cellStyle_test,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    },
    { "headerName": "Mth_2_$",
      "field": "Month_2_$",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueGetter": "parseFloat((data.Month_2_percent - data.Month_1_percent)/100 * data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
  ],
  "debug":True,
  "onCellValueChanged": js,
  # "enableCellChangeFlash": True
}


st.markdown('### Cashflow Forecast')

use_key = st.sidebar.checkbox("use key",value=True)
st.sidebar.write(use_key)
reloadData = st.sidebar.checkbox("reload data")
st.sidebar.write(reloadData)

# st.write(grid_data)

if use_key == True:
  grid_response = AgGrid(
      dataframe = grid_data,
      gridOptions = gridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = 'myKey',   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=reloadData,   # data will only refresh when reload_data = True
      # update_mode=GridUpdateMode.SELECTION_CHANGED,
      allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
      )
elif use_key == False:
  grid_response = AgGrid(
      dataframe = grid_data,
      gridOptions = gridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      # key = 'myKey',   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=reloadData,   # data will only refresh when reload_data = True
      # update_mode=GridUpdateMode.SELECTION_CHANGED,
      allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
      )



# st.write(grid_response['data'])

diff = grid_response['data'].compare(grid_data)
# st.write(diff)
if len(diff) > 0:
  col_changed=diff.columns[0]
  col_to_change=col_changed[0]
  row_changed=diff.index[0]
  value=diff.loc[row_changed,col_changed]
  st.write('new value: ',value)
  # st.write(col_changed)
  # st.write('column changed: ', col_to_change)
  # st.write('row changed: ', row_changed)
  st.session_state.grid_data.loc[row_changed,col_to_change]=value
    # calcs()
    # st.experimental_rerun()

# rerun_button = st.button("rerun")



gantt_df = pd.DataFrame([
    dict(Cost_Item="Cost Item 110", Start='2022-01-01', Finish='2022-02-28', complete=50),
    dict(Cost_Item="Cost Item 120", Start='2022-02-01', Finish='2022-04-15', complete=35),
    dict(Cost_Item="Cost Item 230", Start='2022-01-20', Finish='2022-05-3', complete=70),
    dict(Cost_Item="Cost Item 250", Start='2022-01-01', Finish='2022-03-15', complete=20),
    dict(Cost_Item="Cost Item 325", Start='2022-02-01', Finish='2022-06-15', complete=45),
    dict(Cost_Item="Cost Item 410", Start='2022-01-20', Finish='2022-05-3', complete=90)
])

fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Cost_Item", color='complete')
fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
fig.update_layout(
        width=1400,
        height=400,
        margin=dict(
            l=1,
            r=0,
            b=0,
            t=1
            )
        )

st.markdown('### Gantt chart')


st.plotly_chart(fig)

