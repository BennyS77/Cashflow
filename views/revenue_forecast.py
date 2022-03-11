import streamlit as st
from sqlalchemy import create_engine, text, delete
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import numpy as np
from st_aggrid import AgGrid, JsCode
import plotly.express as px
import pandas as pd
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js, showDaysFormatter, editable, cell_style, cell_style2

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
  if 'readDB' not in st.session_state:
    st.session_state.readDB = True
  if 'actualMonths' not in st.session_state:
    st.session_state.actualMonths = 3
  if 'forecastMonths' not in st.session_state:
    st.session_state.forecastMonths = 3
  if 'changedValue' not in st.session_state:
    st.session_state.changedValue = "Timeline"


def initialiseRevenueData():
    revenue_data = pd.DataFrame.from_dict(
                                    {
                                        "claimItem":['1','2','3'],
                                        "claimItemDescription":['Consultants','Site Facilities','Earthworks'],
                                        "contractSum":[2200.0,3100,2700.00],
                                        "claimedToDate":[600,800,200.0],
                                        "startDate":['2020-02-2','2020-02-2','2020-02-2'],
                                        "numDaysDuration":[20,45,65],
                                        "forecastMethod":['Timeline','Timeline','Timeline'],
                                        "Month_0_availDaysInMonth":[25,25,25],
                                        "Month_0_accumPercent":[0,60,0],
                                        "Month_1_availDaysInMonth":[25,25,25],
                                        "Month_1_accumPercent":[0,80,0],
                                        "Month_2_availDaysInMonth":[25,25,25],
                                        "Month_2_accumPercent":[0,100,0],
                                        "Month_3_availDaysInMonth":[25,25,25],
                                        "Month_4_availDaysInMonth":[25,25,25],
                                    }
    )
    revenue_data['startDate'] = pd.to_datetime(revenue_data['startDate'], format="%Y-%m-%d")
    return revenue_data

def calculateRevenueData(grid_data):
#   grid_data = st.session_state.grid_data
  grid_data['ETC'] = grid_data['contractSum'] - grid_data['claimedToDate']
  grid_data['accumPercent'] = grid_data['claimedToDate'] / grid_data['contractSum']*100
  grid_data['percentPerDay'] = (grid_data['ETC'] / grid_data['contractSum'])*100 / grid_data['numDaysDuration']
  grid_data['daysLeft'] = grid_data['numDaysDuration']
  for i in range(st.session_state.forecastMonths):
    grid_data['workDaysInMonth'] = grid_data.apply(lambda x: x['Month_'+str(i)+'_availDaysInMonth'] if x['daysLeft']>x['Month_'+str(i)+'_availDaysInMonth'] else x['daysLeft'], axis=1 )
    try:
        print(grid_data['Month_'+str(i)+'_accumPercent'])
    except:
        grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else 0, axis=1 )
    else:
        grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else x['Month_'+str(i)+'_accumPercent'], axis=1 )
    grid_data['Month_'+str(i)+'_amount'] = (grid_data['Month_'+str(i)+'_accumPercent'] - grid_data['accumPercent'])/100*grid_data['contractSum']
    grid_data['daysLeft'] = grid_data['daysLeft'] - grid_data['workDaysInMonth']
    grid_data['accumPercent'] = grid_data['Month_'+str(i)+'_accumPercent']
  return grid_data

# @st.experimental_memo
def writeToDatabase(grid_data):
    ## SQL - save to database
    grid_data.to_sql(
        table_name,
        st.session_state.engine,
        if_exists='replace',
        index=False,
        dtype={
            "claimItem":String(30),
            "claimDescription":String(30),
            "contractSum":Float,
            "claimedToDate":Float,
            "startDate":DateTime,
            "numDaysDuration":Integer,
            "forecastMethod":String(20),
            "Month_0_availDaysInMonth":Integer,
            "Month_0_accumPercent":Float,
            "Month_1_availDaysInMonth":Integer,
            "Month_1_accumPercent":Float,
            "Month_2_availDaysInMonth":Integer,
            "Month_2_accumPercent":Float,
            "Month_3_availDaysInMonth":Integer,
            "Month_3_accumPercent":Float,
            "Month_4_availDaysInMonth":Integer,
            "Month_4_accumPercent":Float,
        }
    )

# @st.experimental_memo
def readDatabase():
    ## SQL - read whole table from database
    my_query = 'SELECT * FROM '+table_name
    return pd.read_sql(
        my_query,
        st.session_state.engine,
        parse_dates=[
            'startDate'
        ]
    )

def configActualChildren():
  actualChildren=[{"headerName":"","field":"Tot","maxWidth":100,"cellStyle": {'backgroundColor':'rgba(250,250,250,1)'},}]
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
                'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'}
                },
              {
                # 'field': "Month_"+str(i)+"_amount",
                'headerName' : ' %',
                'maxWidth':60,
                'suppressMenu':True,
                "valueFormatter": "parseFloat(value*100).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
                'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'} }
              ]},
    )
  return actualChildren

def configForecastChildren():
  forecastChildren=[{"headerName":"","field":"for","maxWidth":90,"cellStyle": {'backgroundColor':'rgba(250,250,250,1)'},}]
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
                "cellStyle": cell_style2,
                "valueFormatter": 'parseFloat(data.Month_'+str(i)+'_accumPercent).toFixed(1)+"%"'
                },
              { 'field': "Month_"+str(i)+"_amount",
                'headerName' : ' $',
                'maxWidth':100,
                'suppressMenu':True,
                "cellStyle": {'backgroundColor':'rgba(250,250,250,1)'},
                "valueFormatter": 'parseFloat(data.Month_'+str(i)+'_amount).toLocaleString("en",{minimumFractionDigits: 2,  maximumFractionDigits: 2})'
                }
              ]},
    )
  return forecastChildren


def configureGridOptions(): 
  row_class_rules = {
      # "forecast-timeline": "data.forecastMethod == 'Timeline'",
      "forecast-manual": "data.forecastMethod == 'Manual'",
  }
  revenueGridOptions={
    "defaultColDef": {
      # "minWidth": 50,
      # "maxWidth": 120,
      "filter": True,
    #   "resizable": True,
      "sortable": True
    },
    "columnDefs": [
      { 
        "headerName": "Claim Item",
        "field": "claimItem",
        # 'rowGroup':True,
        "minWidth": 110,
        "maxWidth": 110,
        'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'},
        # "hide": True,
      },
      { "headerName": "Description",
        "field": "claimItemDescription",
        "minWidth": 110,
        "maxWidth": 110,
        'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'},
      },
      { "headerName": "Contract Sum",
        "field": "contractSum",
        "minWidth": 90,
        "maxWidth": 90,
        "type": [
          "numericColumn",
          "numberColumnFilter"
        ],
        'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'},
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "Claimed to Date",
        "field": "claimedToDate",
        "minWidth": 90,
        "maxWidth": 90,
        "type": [
          "numericColumn",
          "numberColumnFilter"
        ],
        'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'},
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "ETC",
        "field": "ETC",
        "minWidth": 90,
        "maxWidth": 90,
        "type": [
          "numericColumn",
          "numberColumnFilter"
          ],
        'cellStyle':{'backgroundColor':'rgba(250,250,250,1)'},
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "Forecast Method",
        "field": "forecastMethod",
        "maxWidth": 135,
        'suppressMenu':True,
        "editable": True,
        # "cellStyle": cell_style,
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
        'suppressMenu':True,
        "type": [
          "numericColumn",
          "numberColumnFilter"
          ],
        "cellStyle": cell_style,
        "valueFormatter":showDaysFormatter
      },
      { "headerName": "Actual",
        "field": "Actual",
        "children":configActualChildren()
      },
      { "headerName": "Forecast",
        "openByDefault":True,
        "children":configForecastChildren(),
      },
      
    ],
    "debug":True,
    "rowClassRules":row_class_rules,
    # "onCellValueChanged": js,
    'groupDefaultExpanded':True,
    # 'animateRows':True,
    # "columnHoverHighlight":True,
    # "onCellEditingStarted": 'console.log("cell editing started")',
    # "onCellEditingStopped": 'console.log("cell editing stopped")',
    # "enableCellChangeFlash": True
  }
  custom_css= {
    ".forecast-timeline": {"color": 'rgba(250,250,250,1)'},
    # ".forecast-manual": {"color": "red !important"},
  }
  return revenueGridOptions, custom_css





##########---------- start -----------#############

# pageConfig()

# setSessionData()

st.markdown('## Revenue Forecast')
table_name = 'revenue_table'

newProject = False

if newProject:
    revenue_data = initialiseRevenueData()
    revenue_data = calculateRevenueData(revenue_data)
    writeToDatabase(revenue_data)


time1 = time.time()
revenue_data = readDatabase()
time2 = time.time()

revenueGridOptions, custom_css = configureGridOptions()


grid_response = AgGrid(
      dataframe = revenue_data,
    #   custom_css = custom_css,
      gridOptions = revenueGridOptions, 
      height = 300,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=True,
      key = 'different_key',   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=True,  
      data_return_mode='AS_INPUT',
      update_mode='VALUE_CHANGED',   ## default
    #   update_mode='MODEL_CHANGED',
      allow_unsafe_jscode=True
      )



for_database = calculateRevenueData(grid_response['data'])


time3 = time.time()
writeToDatabase(for_database)
time4 = time.time()


diff = for_database.compare(revenue_data)
if len(diff) > 0:
    st.experimental_rerun()
    # st.button("rerun")


# st.write('The time taken to READ table from database: ', time2-time1)
# st.write('The time taken to WRITE table to database: ', time4-time3)
