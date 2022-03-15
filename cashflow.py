from multiprocessing.sharedctypes import Value
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, text, delete
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import pandas as pd
from st_aggrid import AgGrid, JsCode
from myConfig import pageConfig
import os


def setSessionData():
    if 'company_code' not in st.session_state:
        st.session_state.company_code = "empty"
    if 'job_number' not in st.session_state:
        st.session_state.job_number = "empty"
    if 'start_date' not in st.session_state:
        st.session_state.start_date = 0
    if 'end_date' not in st.session_state:
        st.session_state.end_date = 0
    if 'reporting_date' not in st.session_state:
        st.session_state.reporting_date = 0
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:np22@127.0.0.1:5432/test_database", echo=True)

pageConfig()

setSessionData()


workDaysInMonth=22


root = os.path.join(os.path.dirname(__file__))

dashboards = {
    "Summary": os.path.join(root, "./views/summary.py"),
    "Cost forecast": os.path.join(root, "./views/cost_forecast.py"),
    "Revenue forecast": os.path.join(root, "./views/revenue_forecast.py"),
}

choice_from_url = query_params = st.experimental_get_query_params().get("notSureWhatThisIs", ["Cost"])[0]

index = list(dashboards.keys()).index(choice_from_url)

choice = st.sidebar.radio("View:", list(dashboards.keys()), index=index)


col1, col2 = st.sidebar.columns(2)
with col1:
    st.session_state.company_code = st.selectbox("Company code:",('ccTest','CoolComp','NearlyBroke'))
    st.markdown("#####")
    start_date=datetime.strptime("1/12/2021","%d/%m/%Y")
    st.session_state.start_date = st.date_input("Start date:",value=start_date)
    st.markdown("#####")
    st.session_state.reporting_date = st.date_input("Reporting date:", value=datetime.today())
with col2:
    st.session_state.job_number = st.selectbox("Job number:",('BG700','TST121','WTF001'))
    st.markdown("#####")
    end_date=datetime.strptime("20/6/2022","%d/%m/%Y")
    st.session_state.end_date = st.date_input("End date:", value=end_date)

actualMonths = (
    (st.session_state.reporting_date.year - st.session_state.start_date.year) * 12
    +
    (st.session_state.reporting_date.month - st.session_state.start_date.month)
    + 1
    )

forecastMonths = (
    (st.session_state.end_date.year - st.session_state.reporting_date.year) * 12
    +
    (st.session_state.end_date.month - st.session_state.reporting_date.month)
    + 1
    )


path = dashboards[choice]
with open(path, encoding="utf-8") as code:
    c = code.read()
    exec(c, globals())
