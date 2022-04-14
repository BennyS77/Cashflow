from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
import streamlit as st
from cost_data import getCompanyAndJobList

def pageConfig():
    st.set_page_config(
      page_title="Premier Reports - Cost Forecast",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="expanded"  #expanded" #"collapsed" #auto
    )
    return




def page_layout():
    html_heading = '<h1 style="text-align: left;padding:0px;padding-bottom:0px;margin:0px">Cashflow</h1>'
    html_line = """<hr style="height:2px;padding:0px;margin:0px;border:none;color:#D3D3D3;background-color:#D3D3D3;" /> """
    st.markdown(html_heading, unsafe_allow_html=True)  
    st.markdown(html_line, unsafe_allow_html=True)
    st.sidebar.markdown("# Report details:")
    global company_ph1, job_ph1, reporting_month_ph1, forecast_end_date_ph1, login_container, msg_ph
    company_ph1 = st.sidebar.empty()
    job_ph1 = st.sidebar.empty()
    st.session_state.job_list = ["PD140479", "TMR456", '']
    reporting_month_ph1 = st.sidebar.empty()
    forecast_end_date_ph1 = st.sidebar.empty()
    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    login_container = st.sidebar.container()
    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")
    msg_ph = st.sidebar.empty()
    return

def setSessionData():
    if 'login_confirmed' not in st.session_state:
        st.session_state.login_confirmed = False
    if 'creds' not in st.session_state:
        st.session_state.creds = {}
    # if 'reporting_month' not in st.session_state:
    #     st.session_state.reporting_month = False
    # if 'forecast_end_date' not in st.session_state:
    #     st.session_state.forecast_end_date = False
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
    # if 'job' not in st.session_state:
    #     st.session_state.job = ''
    if 'table_1' not in st.session_state:
        st.session_state.table_1 = []
    if 'forecast_data_table_name' not in st.session_state:
        st.session_state.forecast_data_table_name = ''
    if 'forecast_table_exists' not in st.session_state:
        st.session_state.forecast_table_exists = 'a'
    if 'reporting_month_data_exists' not in st.session_state:
        st.session_state.reporting_month_data_exists = False
    if 'grid_key' not in st.session_state:
        st.session_state.grid_key = 0
    if 'ready_for_grid' not in st.session_state:
        st.session_state.ready_for_grid = False
    if 'engine' not in st.session_state:
        st.session_state.engine = create_engine("postgresql+psycopg2://postgres:NoticePSQL22@127.0.0.1:5432/premier-reports-database", echo=True)
    return


def my_form(credentials):
        st.session_state.login_confirmed = True
        st.session_state.creds = credentials
        st.session_state.company_list, st.session_state.companies_and_jobs = getCompanyAndJobList()


def setLogIn():
    with st.form('credentials', clear_on_submit=True):
        client_id = st.text_input('Client ID:') 
        username = st.text_input('Username:')  
        password = st.text_input('Password:',type="password") 
        client_id = '317016'
        username = 'BenStewart'
        password = 'Woerifjoi439856'
        creds_dict = {"username":client_id+'\\'+username, "password":password}
        st.form_submit_button('Submit', kwargs = dict(credentials = creds_dict), on_click = my_form)
    return










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

