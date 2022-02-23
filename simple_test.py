import streamlit as st
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js, vg_forecastAmount, vg_forecastPercent

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="auto" #"collapsed" #auto
)


# if 'grid_data' not in st.session_state:
    # st.write("initialise dataframe session state with 'actual' data")
    # st.session_state.grid_data = pd.DataFrame.from_dict(
grid_data = pd.DataFrame.from_dict(
                                  {
                                    "EAC":[1000.678,3000],
                                    "ACTD":[600,800.555],
                                    # "ETC":[0,0],
                                    "forecastMethod":["Timeline","Manual"],
                                    "numDays":[40,25],
                                    "f1Amount":[0,0],
                                    "f2Amount":[0,0],
                                    "f1Percent":[0,0],
                                    "f2Percent":[0,0],
                                  }
      )
 
def calcs():
  grid_data['ETC'] = grid_data.EAC - grid_data.ACTD
  # grid_data['forecastAmount']=grid_data.apply(lambda x: x.ETC if x.forecastMethod =='Timeline' else 0, axis =1)


calcs()

grid_data

dateIsEditable = True
percentIsEditable = True

gridOptions={
  "defaultColDef": {
    "minWidth": 50,
    "maxWidth": 100,
    "filter": True,
    "resizable": True,
    "sortable": True
  },
  "columnDefs": [
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
      "cellEditor": 'agRichSelectCellEditor',
      "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
    },
    { "headerName": "Num of Days",
      "field": "numDays",
      "editable": True,
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
    },
    { "headerName": "F1 $",
      "field": "f1Amount",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "F1 %",
      "field": "f1Percent",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "F2 $",
      "field": "f2Amount",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "F2 %",
      "field": "f2Percent",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
  ],
  "debug":True,
  "onCellValueChanged": js
}


st.markdown('### Cashflow Forecast')

use_key = st.sidebar.checkbox("use key")
st.sidebar.write(use_key)
reloadData = st.sidebar.checkbox("reload data")
st.sidebar.write(reloadData)

if use_key == True:
  grid_response = AgGrid(
      dataframe = grid_data,
      gridOptions = gridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = 'myKey',   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=reloadData,   # data will only refresh when reload_data = True
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
      allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
      )



# st.write(grid_response['data'])

diff = grid_response['data'].compare(grid_data)
st.write(diff)
if len(diff) > 0:
  col_changed=diff.columns[0]
  col_to_change=col_changed[0]
  row_changed=diff.index[0]
  value=diff.loc[row_changed,col_changed]
  # st.write('new value: ',value)
  # st.write(col_changed)
  # st.write('column changed: ', col_to_change)
  # st.write('row changed: ', row_changed)
  # st.session_state.grid_data.loc[row_changed,col_to_change]=value
    # calcs()
    # st.experimental_rerun()

rerun_button = st.button("rerun")





