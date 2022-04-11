from operator import truediv
from urllib import response
import streamlit as st
from st_aggrid import AgGrid
from my_config import page_config_and_session_state
from cashflow_functions import page_layout, get_cost_forecast_settings
from cashflow_functions import select_reporting_month, select_forecast_end_date
from cashflow_functions import create_cost_data_for_reporting_month, create_cost_data_table
from cashflow_functions import get_company, get_job, get_cost_estimate_data, get_all_cost_data, get_date_range
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
from aggrid_functions_revenue import configure_revenue_grid_options, config_revenue_forecast_children, config_revenue_actual_children
from aggrid_functions_summary import configure_summary_grid_options
import pandas as pd
import time

def at_the_start():
    global company, company_defined, job, job_defined, cost_estimate_data, estimation_data, historical_data
    global all_cost_data, historical_data, date_range, period_selected, report_period_data, reporting_month
    global cost_forecast_settings, reporting_month_cost_data, forecast_end_date, cost_data_table
    company = st.session_state.company
    company_defined = st.session_state.company_defined
    job = st.session_state.job
    job_defined = st.session_state.job_defined
    cost_estimate_data = st.session_state.cost_estimate_data
    estimation_data = st.session_state.estimation_data
    all_cost_data = st.session_state.all_cost_data
    historical_data = st.session_state.historical_data
    date_range = st.session_state.date_range
    period_selected = st.session_state.period_selected
    report_period_data = st.session_state.report_period_data
    reporting_month = st.session_state.reporting_month
    reporting_month_cost_data = st.session_state.reporting_month_cost_data
    cost_forecast_settings = st.session_state.cost_forecast_settings
    forecast_end_date = st.session_state.forecast_end_date
    cost_data_table = st.session_state.cost_data_table

def at_the_end():
    st.session_state.company = company
    st.session_state.company_defined = company_defined
    st.session_state.job = job
    st.session_state.job_defined = job_defined
    st.session_state.cost_estimate_data = cost_estimate_data
    st.session_state.estimation_data = estimation_data
    st.session_state.all_cost_data = all_cost_data
    st.session_state.historical_data = historical_data
    st.session_state.date_range = date_range
    st.session_state.period_selected = period_selected
    st.session_state.report_period_data = report_period_data
    st.session_state.reporting_month_cost_data = reporting_month_cost_data
    st.session_state.forecast_end_date = forecast_end_date
    st.session_state.cost_forecast_settings = cost_forecast_settings
    st.session_state.cost_data_table = cost_data_table


page_config_and_session_state()
page_layout()

at_the_start()


"""  THE COMPANY  """
if not company_defined:
    # st.write(" Define the company")
    company = get_company()
    company_defined = True



"""  THE JOB  """
if company_defined and not job_defined:
    # st.write(" Define the job")
    job = get_job()
    job_defined = True



"""  GET THE ESTIMATION DATA  """
if job_defined and not estimation_data:
    # st.write(" Get estimation data for job")
    cost_estimate_data = get_cost_estimate_data(job)
    estimation_data = True



"""  GET ALL HISTORICAL DATA  """
if estimation_data and not historical_data:
    # st.write(" Get all historical data for job")
    all_cost_data = get_all_cost_data(company, job)
    date_range = get_date_range(all_cost_data)
    historical_data = True



"""  DEFINE THE REPORTING MONTH  """
if historical_data:
    # st.write(" Defining the reporting month")
    reporting_month = select_reporting_month(date_range)



"""  THE REPORT-PERIOD DATA  """
if reporting_month != "":
    # st.write(" Creating reporting month cost data")
    cost_by_fiscal_period = all_cost_data.copy()
    reporting_month_cost_data = create_cost_data_for_reporting_month(cost_estimate_data, cost_by_fiscal_period, date_range, reporting_month)
    report_period_data = True



"""  THE FORECAST SETTINGS  """
if report_period_data:
    forecast_end_date = select_forecast_end_date()
    cost_forecast_settings = get_cost_forecast_settings(cost_estimate_data, reporting_month, forecast_end_date)
    # st.write(cost_forecast_settings)



"""  THE WHOLE RAW TABLE  -  Everything we need to know to calculate the grid table"""
if len(cost_forecast_settings) > 0:
    cost_data_table = create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, date_range[0], reporting_month, forecast_end_date)


"""  THE WHOLE CALCULATED TABLE"""

"""  DISPLAY IN THE GRID  """

# grid_response = AgGrid(
#             dataframe = grid_cost_data,
#             custom_css = custom_css,
#             gridOptions = gridOptions, 
#             height = grid_height,
#             enable_enterprise_modules=True,
#             fit_columns_on_grid_load=False,
#             key = st.session_state.grid_key,   #- set a key to stop the grid reinitialising when the dataframe changes
#             reload_data=True,  
#             #   reload_data=False,  
#             data_return_mode='AS_INPUT',
#             #   data_return_mode='FILTERED',
#             update_mode='VALUE_CHANGED',   ## default
#             #   update_mode='MODEL_CHANGED',
#             allow_unsafe_jscode=True,
#             theme="light"



"""  DETECT USER CHANGES TO THE GRID  """



# st.write(cost_estimate_data)
# st.write('reporting_month_cost_data')
# st.write(reporting_month_cost_data.head(5))
# st.write('cost_forecast_settings')
# st.write(cost_forecast_settings.head(5))
st.write('cost_data_table')
st.write(cost_data_table)


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