from datetime import datetime
from sqlalchemy import create_engine, text, delete
from sqlalchemy.orm import Session
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import streamlit as st
from st_aggrid import AgGrid, JsCode
import pandas as pd
import time

begin = time.time()

st.set_page_config(
      page_title="Premier Reports - Cashflow Report",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="collapsed"  #expanded" #"collapsed" #auto
  )

if 'key' not in st.session_state:
    st.session_state.key = 0

if 'engine' not in st.session_state:
    ## create the 'engine' object using SQLite (which is in-memory only)
    # engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    ## create engine using PostgreSQL/psycopg2 to connect to Google Cloud SQL. Note: ensure server is running locally
    st.session_state.engine = create_engine("postgresql+psycopg2://postgres:np22@127.0.0.1:5432/test_database", echo=True)


table_name = 'cost_table'

newProject = False

if newProject:
    dataset = pd.DataFrame.from_dict(
                                    {
                                        "costGroup":['1','1','2'],
                                        "costItem":['110','140','210'],
                                        "EAC":[1000.0,3000,2000.00],
                                        "ACTD":[600,800,200.0],
                                        "startDate":['2020-02-2','2020-02-2','2020-02-2'],
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

    dataset['startDate'] = pd.to_datetime(dataset['startDate'], format="%Y-%m-%d")

    ## SQL - save to database
    dataset.to_sql(
        table_name,
        st.session_state.engine,
        if_exists='replace',
        index=False,
        dtype={
            "costGroup":String(30),
            "costItem":String(30),
            "EAC":Float,
            "ACTD":Float,
            "startDate":DateTime,
            "numDaysDuration":Integer,
            "forecastMethod":String(20),
            "Month_0_availDaysInMonth":Integer,
            "Month_0_accumPercent":Float,
            "Month_1_availDaysInMonth":Integer,
            "Month_1_accumPercent":Float,
            "Month_2_availDaysInMonth":Integer,
            "Month_2_accumPercent":Float,
        }
    )

## SQL - read whole table from database
my_query = 'SELECT * FROM '+table_name
df_read = pd.read_sql(
    my_query,
    st.session_state.engine,
    parse_dates=[
        'startDate'
    ]
)

gridOptions={
    "defaultColDef": {
      "filter": True,
      "resizable": True,
      "sortable": True
    },
    "columnDefs": [
      { "headerName": "costItem",
        "field": "costItem",
        "maxWidth": 95,
      },
      { "headerName": "EAC",
        "field": "EAC",
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "ACTD",
        "field": "ACTD",
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "start date",
        "field": "startDate",
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "Forecast Method",
        "field": "forecastMethod",
        "editable": True,
        "cellEditor": 'agRichSelectCellEditor',
        "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
      },
      { "headerName": "Days",
        "field": "numDaysDuration",
        "editable": True,
      },
        { "headerName": "Month_0_accumPercent",
        "field": "Month_0_accumPercent",
        "editable": True,
      },
    ],
    "debug":True,
    # "onCellValueChanged": js,
  }


grid_response = AgGrid(
      dataframe = df_read,
      # custom_css = custom_css,
      gridOptions = gridOptions, 
      height = 200,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = st.session_state.key,   #- set a key to stop the grid reinitialising when the dataframe changes
      reload_data=False,  
      data_return_mode='AS_INPUT',
      update_mode='VALUE_CHANGED',   ## default
    #   update_mode='MODEL_CHANGED',
      allow_unsafe_jscode=True
      )


st.write(grid_response['data'])




startChange = time.time()
# dataset.at[2,'forecastMethod']=myValue
dataset=grid_response['data']
## SQL - update database
dataset.to_sql(
    table_name,
    st.session_state.engine,
    if_exists='replace',
    index=False,
    dtype={
        "costGroup":String(30),
        "costItem":String(30),
        "EAC":Float,
        "ACTD":Float,
        "startDate":DateTime,
        "numDaysDuration":Integer,
        "forecastMethod":String(20),
        "Month_0_availDaysInMonth":Integer,
        "Month_0_accumPercent":Float,
        "Month_1_availDaysInMonth":Integer,
        "Month_1_accumPercent":Float,
        "Month_2_availDaysInMonth":Integer,
        "Month_2_accumPercent":Float,
    }
)
endChange = time.time()
st.write('Time taken to update database = ', endChange-startChange)










# myValue = st.text_input('input value', key='myinput')
# myValue = grid_response['data']
# st.write(myValue)
# st.button('change forecast method', key='button', on_click=changeTheValue, args=(myValue, ))


end = time.time()
st.write('Time taken = ',end-begin)