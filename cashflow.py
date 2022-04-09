from operator import truediv
from urllib import response
import streamlit as st
from my_config import page_config_and_session_state
from cashflow_functions import page_layout, get_cost_forecast_settings
from cashflow_functions import select_reporting_month
from cashflow_functions import create_cost_table_for_report_period
from cashflow_functions import get_company, get_job, get_cost_estimate_data, get_historical_cost_data, get_date_range
import pandas as pd
import time

def at_the_start():
    global company, company_defined, job, job_defined, cost_estimate_data, estimation_data, historical_data
    global historical_cost_data, historical_data, date_range, period_selected, report_period_data, reporting_month
    global report_period_cost_data
    company = st.session_state.company
    company_defined = st.session_state.company_defined
    job = st.session_state.job
    job_defined = st.session_state.job_defined
    cost_estimate_data = st.session_state.cost_estimate_data
    estimation_data = st.session_state.estimation_data
    historical_cost_data = st.session_state.historical_cost_data
    historical_data = st.session_state.historical_data
    date_range = st.session_state.date_range
    period_selected = st.session_state.period_selected
    report_period_data = st.session_state.report_period_data
    reporting_month = st.session_state.reporting_month
    report_period_cost_data = st.session_state.report_period_cost_data

def at_the_end():
    st.session_state.company = company
    st.session_state.company_defined = company_defined
    st.session_state.job = job
    st.session_state.job_defined = job_defined
    st.session_state.cost_estimate_data = cost_estimate_data
    st.session_state.estimation_data = estimation_data
    st.session_state.historical_cost_data = historical_cost_data
    st.session_state.historical_data = historical_data
    st.session_state.date_range = date_range
    st.session_state.period_selected = period_selected
    st.session_state.report_period_data = report_period_data
    st.session_state.report_period_cost_data = report_period_cost_data



page_config_and_session_state()
page_layout()

at_the_start()


"""  THE COMPANY  """
if not company_defined:
    st.write(" Define the company")
    company = get_company()
    company_defined = True



"""  THE JOB  """
if company_defined and not job_defined:
    st.write(" Define the job")
    job = get_job()
    job_defined = True



"""  THE ESTIMATION DATA  """
if job_defined and not estimation_data:
    st.write(" Get estimation data for job")
    cost_estimate_data = get_cost_estimate_data(job)
    estimation_data = True



"""  THE HISTORICAL DATA  """
if estimation_data and not historical_data:
    st.write(" Get historical data for job")
    historical_cost_data = get_historical_cost_data(company, job)
    date_range = get_date_range(historical_cost_data)
    historical_data = True



"""  THE REPORT PERIOD  """
if historical_data:
    select_reporting_month(date_range)



"""  THE REPORT-PERIOD DATA  """
if reporting_month != "":
    cost_by_fiscal_period = historical_cost_data.copy()
    report_period_cost_data = create_cost_table_for_report_period(cost_estimate_data, cost_by_fiscal_period, date_range, reporting_month)
    report_period_data = True



"""  THE FORECAST SETTINGS  """
if report_period_data:
    cost_forecast_settings = get_cost_forecast_settings()



"""  THE WHOLE FORECAST TABLE  - as stored in the database. Everything we need to know to calculate the grid table"""



"""  THE WHOLE CALCULATED TABLE  """



"""  DISPLAY IN THE GRID  """



"""  DETECT USER CHANGES TO THE GRID  """



# st.write(cost_estimate_data)
st.write(report_period_cost_data)



st.button("rerun")

at_the_end()







# select_company_and_job(testing)



# """  
#     IF JOB CHOSEN - GENERATE ESTIMATE DATA. 
# """
# if st.session_state.job:
#     generate_cost_estimate_data()
#     """  Division  |  Cost_Item  |  Cost_Item_Description  |  EAC  """



#     """ 
#         AFTER GENERATING ESTIMATE DATA - GENERATE ACTUAL DATA 
#     """
#     if len(st.session_state.cost_estimate_data) > 0:
#         generate_all_monthly_cost_data()
#         # st.write(st.session_state.all_monthly_cost_data)
#         generate_job_date_range()
#         # st.write(st.session_state.job_date_range)
#         st.session_state.ready_for_custom_range_of_data = True



# """  
#     CALCULATE DATA TABLE BASED ON SELECTED PERIOD
# """
# if st.session_state.ready_for_custom_range_of_data:
#     select_reporting_month()
#     if st.session_state.reporting_month:
#         calculate_selected_monthly_cost_data()
#         select_forecast_end_date()
#         if not st.session_state.forecast_settings_exist:
#             get_forecast_settings()






# st.write(st.session_state.selected_monthly_cost_data)
# st.write(st.session_state.forecast_settings)

# if not st.session_state.login_confirmed:
#     user_login()


# if st.session_state.login_confirmed:
#     cost_by_fiscal_period = get_JobCostByFiscalPeriod()
#     # cost_estimate_data = get_JobReportByCostItemAndCostTypes()
#     # st.write(len(cost_by_fiscal_period))
#     st.write(cost_by_fiscal_period)
    # st.write(len(cost_estimate_data))
    # st.write(cost_estimate_data)

#     st.session_state.all_cost_data = generate_cost_data()


# if st.session_state.cost_data_retrieved:
#     select_reporting_month()


# if st.session_state.reporting_month:
#     calculate_cost_data_for_the_grid()
#     # st.write(cost_data)







"""   Return: 'all_cost_data' and 'date_range'   """






"""
    """



"""  If 'all cost data' AND NOT 'job'   --> return 'job' list  """

"""  If 'job' AND NOT 'reporting month'  --> return 'reporting month' list """

"""  If 'reporting month' AND NOT 'cost forecast settings'  --> return 'cost forecast settings' """

"""  If 'ready for cost calculations'  --> return calculated 'grid cost data' """

"""  If 'ready for cost graph' --> return updated 'cost graph ' """

"""  If 'ready for grid'  -->  return cost grid """

"""  If 'changes to the cost grid'  -->  return updated 'cost forecast settings"""

# st.write(company_and_job_names)
# st.write(job_cost_by_fiscal_period)
# st.write(st.session_state.all_cost_data)
# st.write(st.session_state.date_range)



# st.write('revenue_clicked: ', st.session_state.revenue_clicked)
# st.write('summary_clicked:', st.session_state.summary_clicked)