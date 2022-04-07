from datetime import datetime
from dateutil.relativedelta import relativedelta
from jinja2 import Undefined
from sqlalchemy import create_engine
import streamlit as st


def page_config_and_session_state():
    """
        Set Page Configuration and Session State variables
    """

    st.set_page_config(
      page_title="Premier Reports - Cost Forecast",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="expanded"  #expanded" #"collapsed" #auto
    )

    if 'login_confirmed' not in st.session_state:
        st.session_state.login_confirmed = False
    if 'creds' not in st.session_state:
        st.session_state.creds = {}
    if 'company_list' not in st.session_state:
        st.session_state.company_list = []
    if 'cost_data' not in st.session_state:
        st.session_state.cost_data = 0
    if 'date_range' not in st.session_state:
        st.session_state.date_range = []
    if 'job_list' not in st.session_state:
        st.session_state.job_list = []
    if 'companies_and_jobs' not in st.session_state:
        st.session_state.companies_and_jobs = []
    if 'table_1' not in st.session_state:
        st.session_state.table_1 = []
    if 'forecast_data_table_name' not in st.session_state:
        st.session_state.forecast_data_table_name = ''
    if 'forecast_table_exists' not in st.session_state:
        st.session_state.forecast_table_exists = None
    if 'reporting_month_data_exists' not in st.session_state:
        st.session_state.reporting_month_data_exists = None
    if 'grid_key' not in st.session_state:
        st.session_state.grid_key = 0
    if 'ready_for_grid' not in st.session_state:
        st.session_state.ready_for_grid = False
    if 'for_testing' not in st.session_state:
        st.session_state.for_testing = False
    if 'new_session' not in st.session_state:
        st.session_state.new_session = True
    if 'revenue_amounts' not in st.session_state:
        st.session_state.revenue_amounts = []
    if 'cost_clicked' not in st.session_state:
        st.session_state.cost_clicked = True
    if 'revenue_clicked' not in st.session_state:
        st.session_state.revenue_clicked = False
    if 'summary_clicked' not in st.session_state:
        st.session_state.summary_clicked = False
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:NoticePSQL22@127.0.0.1:5432/premier-reports-database", echo=True)
    return


















# class report_details:
#     def __init__(self, company_code, job_number, start_date, end_date, reporting_date):
#         self.company_code = company_code
#         self.job_number = job_number
#         self.start_date = start_date
#         self.end_date = end_date
#         self.reporting_date = reporting_date

#     def forecast_months(self):
#         return relativedelta(self.end_date, self.reporting_date).months

