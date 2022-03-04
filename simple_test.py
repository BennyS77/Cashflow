import streamlit as st
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode
import plotly.express as px
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js, cellEditorSelector, cellStyle_test,showDaysFormatter, editable

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="collapsed"  #expanded" #"collapsed" #auto
)

if 'key' not in st.session_state:
  st.session_state.key = 0
if 'check' not in st.session_state:
  st.session_state.check = 0

st.session_state.check = st.session_state.check + 1

# st.write("key:", st.session_state.key)
# st.write("session state check:", st.session_state.check)

if 'grid_data' not in st.session_state:
  st.session_state.grid_data = pd.DataFrame.from_dict(
                                  {
                                    "costItem":['110','140','210'],
                                    "EAC":[1000.0,3000,2000.00],
                                    "ACTD":[600,800,200.0],
                                    # "ETC":[0,0,0],
                                    "numDaysDuration":[20,45,65],
                                    # "actual_$":[600,800,200.0],
                                    # "percentPerDay":[0,0,0],
                                    "forecastMethod":['Timeline','Manual','Timeline'],
                                    "Month_0_availDaysInMonth":[25,25,25],
                                    "Month_0_accumPercent":[0,60,0],
                                    # "Month_0_amount":[0,0,0],
                                    "Month_1_availDaysInMonth":[25,25,25],
                                    "Month_1_accumPercent":[0,80,0],
                                    # "Month_1_amount":[0,0,0],
                                    "Month_2_availDaysInMonth":[25,25,25],
                                    "Month_2_accumPercent":[0,100,0],
                                    # "Month_2_amount":[0,0,0],
                                  }
  )

if 'actualMonths' not in st.session_state:
  st.session_state.actualMonths = 3
if 'forecastMonths' not in st.session_state:
  st.session_state.forecastMonths = 3
if 'changedValue' not in st.session_state:
  st.session_state.changedValue = "Timeline"

grid_data = st.session_state.grid_data

grid_data['ETC'] = grid_data['EAC'] - grid_data['ACTD']
grid_data['accumPercent'] = grid_data['ACTD'] / grid_data['EAC']*100
grid_data['percentPerDay'] = (grid_data['ETC'] / grid_data['EAC'])*100 / grid_data['numDaysDuration']
grid_data['daysLeft'] = grid_data['numDaysDuration']

for i in range(3):
  grid_data['workDaysInMonth'] = grid_data.apply(lambda x: x['Month_'+str(i)+'_availDaysInMonth'] if x['daysLeft']>x['Month_'+str(i)+'_availDaysInMonth'] else x['daysLeft'], axis=1 )
  grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else x['Month_'+str(i)+'_accumPercent'], axis=1 )
  grid_data['Month_'+str(i)+'_amount'] = (grid_data['Month_'+str(i)+'_accumPercent'] - grid_data['accumPercent'])/100*grid_data['EAC']
  grid_data['daysLeft'] = grid_data['daysLeft'] - grid_data['workDaysInMonth']
  grid_data['accumPercent'] = grid_data['Month_'+str(i)+'_accumPercent']



st.session_state.grid_data = grid_data
# st.write(st.session_state.changedValue)
# st.write(grid_data)


forecastChildren=[{"headerName":"","field":"for","minWidth":100}]

for i in range(0,st.session_state.forecastMonths,1):
    month= 'Month: '+str(i+1)
    forecast_dollars = 'F $'
    forecast_percent = 'F %'
    forecastChildren.append(
        {"headerName" : month+' - Claim '+str(i+1),
        'columnGroupShow': 'open',
         "children":[
            { 'field': "Month_"+str(i)+"_accumPercent",
              'headerName' : ' %',
              'maxWidth':80,
              'suppressMenu':True,
              "editable": editable,
              "cellStyle": cellStyle_test,
              "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
              },
            { 'field': "Month_"+str(i)+"_amount",
              'headerName' : ' $',
              'maxWidth':100,
              'suppressMenu':True,
              "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
              }
            ]},
  )

gridOptions={
  "defaultColDef": {
    "minWidth": 50,
    "maxWidth": 120,
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
      "field": "numDaysDuration",
      "editable": True,
      "maxWidth": 75,
      "hide":True,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
    },
    { "headerName": "Days",
      "editable": True,
      "maxWidth": 75,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter":showDaysFormatter
    },
    { "headerName": "Forecast",
      "field": "Forecast",
      "children":forecastChildren
    },
    # { "headerName": "Mth_0_%",
    #   "field": "Month_0_accumPercent",
    #   "editable": editable,
    #   "cellStyle": cellStyle_test,
    #   "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    # },
    # { "headerName": "Mth_0_$",
    #   "field": "Month_0_amount",
    #   "type": [
    #     "numericColumn",
    #     "numberColumnFilter"
    #     ],
    #   "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    # },
    # { "headerName": "Mth_1_%",
    #   "field": "Month_1_accumPercent",
    #   "editable": editable,
    #   "cellStyle": cellStyle_test,
    #   "type": [
    #     "numericColumn",
    #     "numberColumnFilter"
    #     ],
    #   "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    # },
    # { "headerName": "Mth_1_$",
    #   "field": "Month_1_amount",
    #   "type": [
    #     "numericColumn",
    #     "numberColumnFilter"
    #     ],
    #   "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    # },
    # { "headerName": "Mth_2_%",
    #   "field": "Month_2_accumPercent",
    #   "editable": editable,
    #   "cellStyle": cellStyle_test,
    #   "type": [
    #     "numericColumn",
    #     "numberColumnFilter"
    #     ],
    #   "valueFormatter": "parseFloat(value).toFixed(1)+'%'"
    # },
    # { "headerName": "Mth_2_$",
    #   "field": "Month_2_amount",
    #   "type": [
    #     "numericColumn",
    #     "numberColumnFilter"
    #     ],
    #   "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    # },
  ],
  "debug":True,
  "onCellValueChanged": js,
  # "columnHoverHighlight":True,
  # "onCellEditingStarted": 'console.log("cell editing started")',
  # "onCellEditingStopped": 'console.log("cell editing stopped")',
  # "enableCellChangeFlash": True
}


st.markdown('### Cashflow Forecast')

use_key = st.sidebar.checkbox("use key",value=True)
st.sidebar.write(use_key)
reloadData = st.sidebar.checkbox("reload data",value=True)
st.sidebar.write(reloadData)


if use_key == True:
  grid_response = AgGrid(
      dataframe = grid_data,
      gridOptions = gridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = st.session_state.key,   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=reloadData,   # data will only refresh when reload_data = True
      data_return_mode='AS_INPUT',
      # update_mode='VALUE_CHANGED',   ## default
      update_mode='MODEL_CHANGED',
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
  # st.write(type(col_changed))
  col_to_change=col_changed[0]
  # st.write(type(col_to_change))
  # if 'ount' in col_to_change :
    # st.write(col_to_change)
  row_changed=diff.index[0]
  st.session_state.changedValue = diff.loc[row_changed,col_changed]
  # st.write('grid response value: ',st.session_state.changedValue)
  # st.write(col_changed)
  # st.write('column changed: ', col_to_change)
  # st.write('row changed: ', row_changed)
  st.session_state.grid_data.loc[row_changed,col_to_change]=st.session_state.changedValue
  if st.session_state.changedValue == "Timeline":
    st.session_state.key = st.session_state.key + 1
  if col_to_change == 'forecastMethod' or 'ount' not in col_to_change :
    st.experimental_rerun()
  # rerun_button = st.button("rerun")



