from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import streamlit as st

def pageConfig():
  st.set_page_config(
      page_title="Premier Reports - Cashflow Report",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="expanded"  #expanded" #"collapsed" #auto
  )

def setSessionData():
    if 'count' not in st.session_state:
        st.session_state.count = 0
    if 'company_code' not in st.session_state:
        st.session_state.company_code = ""
    if 'job_number' not in st.session_state:
        st.session_state.job_number = ""
    
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:np22@127.0.0.1:5432/test_database", echo=True)
    # if 'report_details' not in st.session_state:
    #     st.session_state.report_details = report_details(
    #         'G01',
    #         'PD140479',
    #         datetime.strptime("16/6/2020","%d/%m/%Y"),
    #         datetime.strptime("30/6/2022","%d/%m/%Y"),
    #         datetime.strptime("28/2/2022","%d/%m/%Y"),
    #         # datetime.today() - relativedelta(months=1)
    #     )
    # return st.session_state.report_details


# def setSidebar(r1, company_list, job_list):
#     st.sidebar.markdown("## Report details")
#     col1, col2 = st.sidebar.columns([2,1])
#     with col1:
#         r1.company_code = st.selectbox("Company code:",company_list)
#         # st.markdown("#####")
#         r1.job_number = st.selectbox("Job number:",job_list)
#         r1.end_date = st.date_input("End date:", value=r1.end_date)
#         st.markdown("#####")
#         r1.reporting_date = st.date_input("Reporting date:", value=r1.reporting_date)
#     return r1



# class report_details:
#     def __init__(self, company_code, job_number, start_date, end_date, reporting_date):
#         self.company_code = company_code
#         self.job_number = job_number
#         self.start_date = start_date
#         self.end_date = end_date
#         self.reporting_date = reporting_date

#     def forecast_months(self):
#         return relativedelta(self.end_date, self.reporting_date).months

