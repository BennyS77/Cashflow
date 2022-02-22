import streamlit as st
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode, GridUpdateMode, DataReturnMode
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="auto" #"collapsed" #auto
)

if 'grid_key' not in st.session_state:
    st.session_state.grid_key = 0

if 'grid_data' not in st.session_state:
    st.write("starting from scratch")
    st.session_state.grid_data = pd.DataFrame.from_dict({"EAC":[1000.678,3000],
                                                         "ACTD":[600,800.555],
                                                         "ETC":[0,0],
                                                         "forecastMethod":["Timeline","Manual"],
                                                         "startDate":[0,0],
                                                         "endDate":[0,0],
                                                         "f1_dollars":[0,0],
                                                         "f1_percent":[0,0],
                                                         "f2_dollars":[0,0],
                                                         "f2_percent":[0,0],
                                                         "f3_dollars":[0,0],
                                                         "f3_percent":[0,0]})


project_code = 'PD140479'
startDate = '5/1/2021'
endDate = '20/8/2021'
reportDate = '20/5/2021'
startDate_obj = datetime.strptime(startDate, '%d/%m/%Y')
endDate_obj = datetime.strptime(endDate, '%d/%m/%Y')
reportDate_obj = datetime.strptime(reportDate, '%d/%m/%Y')
actualDays=(endDate_obj-startDate_obj).days
actualMonths=endDate_obj.month-startDate_obj.month
forecastMonths=endDate_obj.month-reportDate_obj.month


def calcs():
    st.session_state.grid_data['ETC'] = st.session_state.grid_data['EAC'] - st.session_state.grid_data['ACTD']
    st.session_state.grid_data['startDate']=st.session_state.grid_data.apply(lambda x: startDate_obj.strftime('%d/%m/%Y') if x.forecastMethod =='Timeline' else '-', axis =1)
    st.session_state.grid_data['endDate']=st.session_state.grid_data.apply(lambda x: endDate_obj.strftime('%d/%m/%Y') if x.forecastMethod =='Timeline' else '-', axis =1)

    def dollars(ETC,method, report, end, percent):
        if method=="Timeline":
            end_date = datetime.strptime(end, '%d/%m/%Y')
            amount= ETC/(end_date.month - report.month)
        elif method=="Manual":
            amount=float(percent)*float(ETC)
        return amount

    def percent(ETC,method, dollars, percent):
        if method=="Timeline" and ETC!=0:
            percentage = dollars/ETC
        elif method=="Manual":
            percentage = percent
        return percentage

    st.session_state.grid_data['f1_dollars']=st.session_state.grid_data.apply(lambda row: dollars(row.ETC, row.forecastMethod, reportDate_obj, row.endDate, row.f1_percent), axis=1)
    st.session_state.grid_data['f1_percent']=st.session_state.grid_data.apply(lambda row: percent(row.ETC, row.forecastMethod, row.f1_dollars, row.f1_percent), axis=1)
    # st.session_state.grid_data['forecast2']=st.session_state.grid_data.apply(lambda row: f1(row.ETC, row.forecastMethod, reportDate_obj, row.endDate), axis=1)
    # st.session_state.grid_data['forecast3']=st.session_state.grid_data.apply(lambda row: f1(row.ETC, row.forecastMethod, reportDate_obj, row.endDate), axis=1)

st.write(st.session_state.grid_data)
calcs()
st.write(st.session_state.grid_data)

dateIsEditable = True
percentIsEditable = True

gridOptions={
  "defaultColDef": {
    "minWidth": 50,
    "maxWidth": 100,
    "editable": True,
    "filter": True,
    "resizable": True,
    "sortable": True
  },
  "columnDefs": [
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
      "valueFormatter": "parseFloat(data.EAC-data.ACTD).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Forecast Method",
      "field": "forecastMethod",
      "editable": True,
      "cellEditor": 'agRichSelectCellEditor',
      "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
    },
    { "headerName": "Start Date",
      "field": "startDate",
      "editable": dateIsEditable
    },
    { "headerName": "End Date",
      "field": "endDate",
      "editable": dateIsEditable
    },
    { "headerName": "Forecast $",
      "field": "f1_dollars",
    },
    { "headerName": "Forecast %",
      "field": "f1_percent",
      "editable": percentIsEditable
    },
    { "headerName": "Forecast 2",
      "field": "forecast2",
    },
    { "headerName": "Forecast 3",
      "field": "forecast3",
    },
  ],
#   "onCellValueChanged": js,
  "debug":True,
}

# gridOptions['defaultColDef']['minWidth']=88

st.markdown('### Cashflow Forecast')

grid_response = AgGrid(
    dataframe = st.session_state.grid_data,
    gridOptions = gridOptions, 
    height = 200,
    enable_enterprise_modules=True,
    fit_columns_on_grid_load=False,
    reload_data=False,
    # key = st.session_state.grid_key,
    # data_return_mode = DataReturnMode.AS_INPUT,
    # update_mode = GridUpdateMode.MANUAL,
    # update_mode=GridUpdateMode.VALUE_CHANGED,
    # update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
    )

st.write(grid_response['data'])

diff = grid_response['data'].compare(st.session_state.grid_data)
st.write(diff)

if len(diff)>0:
    col_changed=diff.columns[0]
    col_to_change=col_changed[0]
    row_changed=diff.index[0]
    value=diff.loc[row_changed,col_changed]
    # st.write(diff)
    st.write(value)
    # st.write(col_changed)
    # st.write(col_to_change)
    # st.write(row_changed)
    st.session_state.grid_data.loc[row_changed,col_to_change]=value
    calcs()
    st.experimental_rerun()

# def rerun():
#     st.experimental_rerun()

rerun_button = st.button("rerun")





