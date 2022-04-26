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
      initial_sidebar_state="auto"  #expanded" #"collapsed" #auto
    )
    if 'cost_clicked' not in st.session_state:
        st.session_state.cost_clicked = True
    if 'revenue_clicked' not in st.session_state:
        st.session_state.revenue_clicked = False
    if 'summary_clicked' not in st.session_state:
        st.session_state.summary_clicked = False
    # if 'company' not in st.session_state:
    #     st.session_state.company = ""
    if 'company_defined' not in st.session_state:
        st.session_state.company_defined = False
    if 'job' not in st.session_state:
        st.session_state.job = ""
    if 'job_defined' not in st.session_state:
        st.session_state.job_defined = False
    if 'cost_estimate_data' not in st.session_state:
        st.session_state.cost_estimate_data = None
    if 'estimation_data_defined' not in st.session_state:
        st.session_state.estimation_data_defined = False
    if 'all_cost_data' not in st.session_state:
        st.session_state.all_cost_data = None
    if 'historical_data_defined' not in st.session_state:
        st.session_state.historical_data_defined = False
    if 'date_range' not in st.session_state:
        st.session_state.date_range = None
    if 'period_selected' not in st.session_state:
        st.session_state.period_selected = False
    if 'reporting_month' not in st.session_state:
        st.session_state.reporting_month = ""
    if 'reporting_month_data_defined' not in st.session_state:
        st.session_state.reporting_month_data_defined = False
    if 'reporting_month_cost_data' not in st.session_state:
        st.session_state.reporting_month_cost_data = None
    if 'cost_forecast_settings' not in st.session_state:
        st.session_state.cost_forecast_settings = None
    if 'cost_forecast_settings_defined' not in st.session_state:
        st.session_state.cost_forecast_settings_defined = False
    if 'forecast_end_date' not in st.session_state:
        st.session_state.forecast_end_date = None
    if 'show_forecast_end_date' not in st.session_state:
        st.session_state.show_forecast_end_date = False
    if 'cost_data_table' not in st.session_state:
        st.session_state.cost_data_table = None
    if 'ready_for_grid' not in st.session_state:
        st.session_state.ready_for_grid = False
    if 'grid_key' not in st.session_state:
        st.session_state.grid_key = 0
    if 'forecast_data_table_name' not in st.session_state:
        st.session_state.forecast_data_table_name = ''
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:NoticePSQL22@127.0.0.1:5432/premier-reports-database", echo=True)
    if 'login_confirmed' not in st.session_state:
        st.session_state.login_confirmed = False
    if 'creds' not in st.session_state:
        st.session_state.creds = {}
    if 'company_list' not in st.session_state:
        st.session_state.company_list = []
    if 'job_list' not in st.session_state:
        st.session_state.job_list = []
    if 'grid_cost_data' not in st.session_state:
        st.session_state.grid_cost_data = 0
    if 'session_number' not in st.session_state:
        st.session_state.session_number = 0
    if 'show_reporting_month' not in st.session_state:
        st.session_state.show_reporting_month = False
    if 'reporting_month_list' not in st.session_state:
        st.session_state.reporting_month_list = []
    

  
    
 

    # # if 'for_testing' not in st.session_state:
    # #     st.session_state.for_testing = False
 
    # if 'revenue_amounts' not in st.session_state:
    #     st.session_state.revenue_amounts = []
    
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

