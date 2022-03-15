import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, text, delete
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import pandas as pd
from dateutil.relativedelta import relativedelta
from cost_data import getCostSummaryData, getEACdata, processData, calculations
from myConfig import pageConfig
from st_aggrid import AgGrid, JsCode
from myConfig import pageConfig, report_details
import numpy as np




def writeToDatabase(baseCostData, table_name):
    # st.write(f"Write to database: {table_name}")
    dtype_dict={}
    for item in baseCostData.columns:
        dtype_dict.update({item:Float})
    dtype_dict.update({
            "costGroup":String(30),
            "costitem":String(30),
            "Description":String(50),
            "startDate":DateTime,
            "endDate":DateTime,
            "forecastmethod":String(20),
    })
    baseCostData.to_sql(
        table_name,
        st.session_state.engine,
        if_exists='replace',
        index=False,
        dtype=dtype_dict
    )
    # st.write(f'Successfully wrote to database: {table_name}')
    return 


def readDatabase(table_name):
    # st.write(f"Reading table: {table_name}")
    my_query = 'SELECT * FROM '+ table_name
    data = pd.read_sql(
        my_query,
        st.session_state.engine,
        parse_dates=[
            'startDate',
            'endDate'
        ]
    )
    # st.write(f'Successfully read from database: {table_name}')
    return data 



def updateTable(table_name, col, new_value, where_col, where_value):
    sql_query = """
        UPDATE """+table_name+"""
        SET """+col+""" = """+new_value+"""
        WHERE """+where_col+""" = """+where_value
    with st.session_state.engine.begin() as conn:
        conn.execute(sql_query)



