import streamlit as st
# from datetime import datetime
# from sqlalchemy import create_engine, text, delete
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import pandas as pd
# from dateutil.relativedelta import relativedelta
# from cost_data import getCostSummaryData, getEACdata, processData
# from myConfig import pageConfig
# from st_aggrid import AgGrid, JsCode
# import numpy as np

def drop_table(table_name):
    st.sidebar.write(f""" DELETING table '{table_name}' from the database... """)
    sql_query = """DROP TABLE """+table_name
    st.write(sql_query)
    with st.session_state.engine.begin() as conn:
        conn.execute(sql_query)
    st.sidebar.write(f"DELETED table: '{table_name}' from the database.")
    return


def write_table_to_database(report_data, table_name):
    # st.sidebar.write(f""" WRITING table '{table_name}' to the database... """)
    dtype_dict={}
    for item in report_data.columns:
        dtype_dict.update({item:Float})
    dtype_dict.update({
            "Division":String(40),
            "cost_item":String(30),
            "Cost_Item_Description":String(60),
            "reporting_month":DateTime,
            "item_start_date":DateTime,
            "item_end_date":String(25),
            "forecast_method":String(25),
    })
    report_data.to_sql(
        table_name,
        st.session_state.engine,
        if_exists='replace',
        index=False,
        dtype=dtype_dict
    )
    # st.sidebar.write(f"WROTE table '{table_name}' to the database.")
    return 


## 3
def read_table_from_database(table_name):
    # st.sidebar.write(f""" 3. READING table '{table_name}' from the database... """)
    my_query = 'SELECT * FROM "' + table_name+'"'
    data = pd.read_sql(
        my_query,
        st.session_state.engine,
        parse_dates=[
            "reporting_month",
            "item_start_date",
            "item_end_date",
        ]
    )
    # st.sidebar.write(f"3. Done.")
    return data 


def table_names():
    sql_query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"
    data = pd.read_sql(
        sql_query,
        st.session_state.engine,
    )
    return data



def update_table(table_name, col, new_value, where_col, where_value, where_col2, where_value2):
    table_name='"'+table_name+'"'
    # new_value ="'"+new_value+"'"
    # where_value ="'"+where_value+"'"
    # where_value2 ="'"+where_value2+"'"
    sql_query = """
        UPDATE """+table_name+"""
        SET """+col+""" = """+new_value+"""
        WHERE """+where_col+""" = """+where_value+""" and """+where_col2+""" = """+where_value2
    # st.sidebar.write(sql_query)
    with st.session_state.engine.begin() as conn:
        conn.execute(sql_query)
    return








def other_update_table(table_name, col, new_value, where_col, where_value):
    sql_query = 'UPDATE "'+table_name+'" SET "forecast_method" = Manual"'
    # WHERE '+where_col+' = "'+where_value+'";'
    st.sidebar.write(sql_query)
    with st.session_state.engine.begin() as conn:
        conn.execute(sql_query)
    return



def writeCostDataToDatabase(baseCostData, table_name):
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
    ### .... Read table_name from the database .... ###
    my_query = 'SELECT * FROM '+ table_name
    data = pd.read_sql(
        my_query,
        st.session_state.engine,
        parse_dates=[
            'startDate',
            'endDate'
        ]
    )
    # st.sidebar.write(f'Successfully read from database: {table_name}')
    return data 






def appendDatabase(forecast_details, table_name):
    """ write the Forecast Details information to the database """
    dtype_dict={}
    for item in forecast_details.columns:
        dtype_dict.update({item:Float})
    dtype_dict.update({
            "cost_item":String(30),
            "reporting_month":DateTime,
            "forecast_end_date":DateTime,
            "item_start_date":DateTime,
            "item_end_date":DateTime,
            "forecast_method":String(20),
    })
    forecast_details.to_sql(
        table_name,
        st.session_state.engine,
        if_exists='append',
        index=False,
        dtype=dtype_dict
    )
    # st.sidebar.write(f'Successfully appended database: {table_name}')
    return 