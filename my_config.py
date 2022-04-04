from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import streamlit as st

def pageConfig():
    st.set_page_config(
      page_title="Premier Reports - Cost Forecast",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="expanded"  #expanded" #"collapsed" #auto
    )
    return

def page_layout():
    col1, col2, col3, col4, col5 = st.columns([2,1,1,1,3])
    with col1:
        st.markdown("## Cost Forecast")
    with col2:
        st.write("Company: ")
        st.write("Job: ")
    with col3:
        company_ph1 = st.empty()
        company_ph1.write(st.session_state.company)
        job_ph1 = st.empty()
        job_ph1.write(st.session_state.job)
    with col4:
        st.write("Reporting Month: ")
        st.write("Forecast End Date: ")
    with col5:
        reporting_month_ph1 = st.empty()
        if st.session_state.reporting_month:
            reporting_month_ph1.write(st.session_state.reporting_month.strftime("%b %Y"))
        forecast_end_date_ph1 = st.empty()
        if st.session_state.forecast_end_date:
            forecast_end_date_ph1.write(st.session_state.forecast_end_date.strftime("%d %b %Y"))
    return

def setSessionData():
    if 'login_confirmed' not in st.session_state:
        st.session_state.login_confirmed = False
    if 'reporting_month' not in st.session_state:
        st.session_state.reporting_month = False
    if 'forecast_end_date' not in st.session_state:
        st.session_state.forecast_end_date = False
        # st.session_state.forecast_end_date = (datetime.today() + relativedelta(months=6)).date()
    if 'company' not in st.session_state:
        st.session_state.company = False
    if 'job' not in st.session_state:
        st.session_state.job = False
    if 'table_1' not in st.session_state:
        st.session_state.table_1 = []
    if 'forecast_table_exists' not in st.session_state:
        st.session_state.forecast_table_exists = False
    if 'reporting_month_data_exists' not in st.session_state:
        st.session_state.reporting_month_data_exists = False
    if 'grid_key' not in st.session_state:
        st.session_state.grid_key = 0
    if 'ready_for_grid' not in st.session_state:
        st.session_state.ready_for_grid = False
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:NoticePSQL22@127.0.0.1:5432/premier-reports-database", echo=True)
    return




def setLogIn():
    def my_form():
        st.session_state.login_confirmed = True
    with st.sidebar.form('creds', clear_on_submit=True):
        client_id = st.text_input('Client ID:') 
        username = st.text_input('Username:')  
        password = st.text_input('Password:',type="password") 
        st.form_submit_button('Submit', on_click = my_form)
        client_id = '317016'
        username = 'BenStewart'
        password = 'Woerifjoi439856'
    return {"username":client_id+'\\'+username, "password":password}










        # st.session_state.engine = create_engine("postgresql+psycopg2://postgres:np22@127.0.0.1:5432/test_database", echo=True)
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

