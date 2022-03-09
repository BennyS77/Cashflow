import streamlit as st
import numpy as np
from st_aggrid import AgGrid, JsCode
import plotly.express as px
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js, showDaysFormatter, editable, cell_style

def pageConfig():
  st.set_page_config(
      page_title="Premier Reports - Cashflow Report",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="collapsed"  #expanded" #"collapsed" #auto
  )

def setSessionData():
  if 'key' not in st.session_state:
    st.session_state.key = 0
  if 'check' not in st.session_state:
    st.session_state.check = 0
  if 'actualMonths' not in st.session_state:
    st.session_state.actualMonths = 3
  if 'forecastMonths' not in st.session_state:
    st.session_state.forecastMonths = 3
  if 'changedValue' not in st.session_state:
    st.session_state.changedValue = "Timeline"
  if 'grid_data' not in st.session_state:
    st.session_state.grid_data = pd.DataFrame.from_dict(
                                  {
                                    "costGroup":[1,1,2],
                                    "costItem":['110','140','210'],
                                    "EAC":[1000.0,3000,2000.00],
                                    "ACTD":[600,800,200.0],
                                    "numDaysDuration":[20,45,65],
                                    "forecastMethod":['Timeline','Manual','Timeline'],
                                    "Month_0_availDaysInMonth":[25,25,25],
                                    "Month_0_accumPercent":[0,60,0],
                                    "Month_1_availDaysInMonth":[25,25,25],
                                    "Month_1_accumPercent":[0,80,0],
                                    "Month_2_availDaysInMonth":[25,25,25],
                                    "Month_2_accumPercent":[0,100,0],
                                  }
  )

def calculations():
  grid_data = st.session_state.grid_data

  grid_data['ETC'] = grid_data['EAC'] - grid_data['ACTD']
  grid_data['accumPercent'] = grid_data['ACTD'] / grid_data['EAC']*100
  grid_data['percentPerDay'] = (grid_data['ETC'] / grid_data['EAC'])*100 / grid_data['numDaysDuration']
  grid_data['daysLeft'] = grid_data['numDaysDuration']
  for i in range(st.session_state.forecastMonths):
    grid_data['workDaysInMonth'] = grid_data.apply(lambda x: x['Month_'+str(i)+'_availDaysInMonth'] if x['daysLeft']>x['Month_'+str(i)+'_availDaysInMonth'] else x['daysLeft'], axis=1 )
    grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else x['Month_'+str(i)+'_accumPercent'], axis=1 )
    grid_data['Month_'+str(i)+'_amount'] = (grid_data['Month_'+str(i)+'_accumPercent'] - grid_data['accumPercent'])/100*grid_data['EAC']
    grid_data['daysLeft'] = grid_data['daysLeft'] - grid_data['workDaysInMonth']
    grid_data['accumPercent'] = grid_data['Month_'+str(i)+'_accumPercent']
  return grid_data

def configActualChildren():
  actualChildren=[{"headerName":"","field":"Tot","minWidth":80}]
  for i in range(0,st.session_state.actualMonths,1):
      actualChildren.append(
          {
          "headerName" : 'Month'+str(i)+' - Claim '+str(i+1),
          'columnGroupShow': 'open',
          "children":[
              {
                # 'field': month+' - Claim '+str(i+1),
                'headerName' : ' $',
                'maxWidth':80,
                'suppressMenu':True,
                "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
                'cellStyle':{'backgroundColor':'lightgrey'}
                },
              {
                # 'field': "Month_"+str(i)+"_amount",
                'headerName' : ' %',
                'maxWidth':60,
                'suppressMenu':True,
                "valueFormatter": "parseFloat(value*100).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
                'cellStyle':{'backgroundColor':'lightgrey'} }
              ]},
    )
  return actualChildren

def configForecastChildren():
  forecastChildren=[{"headerName":"","field":"for","minWidth":100}]
  for i in range(0,st.session_state.forecastMonths,1):
      forecastChildren.append(
          {"headerName" : 'Month: '+str(i+1)+' - Claim '+str(i+1),
          'columnGroupShow': 'open',
          "children":[
              { 'field': "Month_"+str(i)+"_accumPercent",
                'headerName' : ' %',
                'maxWidth':80,
                'suppressMenu':True,
                "editable": editable,
                "cellStyle": cell_style,
                "valueFormatter": 'parseFloat(data.Month_'+str(i)+'_accumPercent).toFixed(1)+"%"'
                },
              { 'field': "Month_"+str(i)+"_amount",
                'headerName' : ' $',
                'maxWidth':100,
                'suppressMenu':True,
                "valueFormatter": 'parseFloat(data.Month_'+str(i)+'_amount).toLocaleString("en",{minimumFractionDigits: 2,  maximumFractionDigits: 2})'
                }
              ]},
    )
  return forecastChildren

def updateSessionData(gr_df):
  diff = gr_df.compare(calculations())
  # st.write(diff)
  if len(diff) > 0:
    col_changed=diff.columns[0]
    col_to_change=col_changed[0]
    row_changed=diff.index[0]
    st.session_state.changedValue = diff.loc[row_changed,col_changed]
    st.session_state.grid_data.loc[row_changed,col_to_change]=st.session_state.changedValue
    if st.session_state.changedValue == "Timeline":
      st.session_state.key = st.session_state.key + 1
    # rerun_button = st.button("rerun")
    if col_to_change == 'forecastMethod' or 'ount' not in col_to_change :
      st.experimental_rerun()

def configureGridOptions():
  row_class_rules = {
      # "forecast-timeline": "data.forecastMethod == 'Timeline'",
      "forecast-manual": "data.forecastMethod == 'Manual'",
  }
  gridOptions={
    "defaultColDef": {
      # "minWidth": 50,
      # "maxWidth": 120,
      "filter": True,
      "resizable": True,
      "sortable": True
    },
    "columnDefs": [
      { 
        "headerName": "Cost Group",
        "field": "costGroup",
        # 'rowGroup':True,
        "maxWidth": 95,
        # "hide": True,
      },
      { "headerName": "Cost Item",
        "field": "costItem",
        "maxWidth": 95,
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
        "maxWidth": 125,
        'suppressMenu':True,
        "editable": True,
        "cellStyle": cell_style,
        "cellEditor": 'agRichSelectCellEditor',
        "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
      },
      { "headerName": "Days",
        "field": "numDaysDuration",
        "editable": True,
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
      { "headerName": "Actual",
        "field": "Actual",
        "children":configActualChildren()
      },
      { "headerName": "Forecast",
        "openByDefault":True,
        "children":configForecastChildren(),
        "maxWidth": 175,
      },
      
    ],
    "debug":True,
    "rowClassRules":row_class_rules,
    "onCellValueChanged": js,
    'groupDefaultExpanded':True,
    'animateRows':True,
    # "columnHoverHighlight":True,
    # "onCellEditingStarted": 'console.log("cell editing started")',
    # "onCellEditingStopped": 'console.log("cell editing stopped")',
    # "enableCellChangeFlash": True
  }
  custom_css= {
    # ".forecast-timeline": {"color": "green !important"},
    ".forecast-manual": {"color": "red !important"},
  }
  return gridOptions, custom_css





##########---------- start -----------#############

pageConfig()

setSessionData()


gridOptions, custom_css = configureGridOptions()


grid_response = AgGrid(
      dataframe = calculations(),
      # custom_css = custom_css,
      gridOptions = gridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = st.session_state.key,   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=True,  
      data_return_mode='AS_INPUT',
      # update_mode='VALUE_CHANGED',   ## default
      update_mode='MODEL_CHANGED',
      allow_unsafe_jscode=True
      )


updateSessionData(grid_response['data'])


