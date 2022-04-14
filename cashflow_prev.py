from datetime import datetime
from operator import truediv
from urllib import response
import streamlit as st
# from st_aggrid import AgGrid
from my_config import page_config_and_session_state
from cashflow_functions import page_layout, get_cost_forecast_settings, display_cost_in_grid
from cashflow_functions import select_reporting_month, select_forecast_end_date, recalculate_cost_forecast_settings
from cashflow_functions import create_cost_data_for_reporting_month, create_cost_data_table
from cashflow_functions import get_company, get_job, get_cost_estimate_data, get_all_cost_data, get_date_range
# from aggrid_functions_revenue import configure_revenue_grid_options, config_revenue_forecast_children, config_revenue_actual_children
# from aggrid_functions_summary import configure_summary_grid_options
import pandas as pd
import time

def at_the_start():
    global company, company_defined, job, job_defined, cost_estimate_data, estimation_data_defined
    global all_cost_data, historical_data_defined, date_range, period_selected, reporting_month_data_defined, reporting_month
    global cost_forecast_settings, reporting_month_cost_data, forecast_end_date, cost_data_table, cost_forecast_settings_defined
    company = st.session_state.company
    company_defined = st.session_state.company_defined
    job = st.session_state.job
    job_defined = st.session_state.job_defined
    cost_estimate_data = st.session_state.cost_estimate_data
    estimation_data_defined = st.session_state.estimation_data_defined
    all_cost_data = st.session_state.all_cost_data
    historical_data_defined = st.session_state.historical_data_defined
    date_range = st.session_state.date_range
    period_selected = st.session_state.period_selected
    reporting_month_data_defined = st.session_state.reporting_month_data_defined
    reporting_month = st.session_state.reporting_month
    reporting_month_cost_data = st.session_state.reporting_month_cost_data
    cost_forecast_settings = st.session_state.cost_forecast_settings
    forecast_end_date = st.session_state.forecast_end_date
    cost_data_table = st.session_state.cost_data_table
    cost_forecast_settings_defined = st.session_state.cost_forecast_settings_defined

def at_the_end():
    st.session_state.company = company
    st.session_state.company_defined = company_defined
    st.session_state.job = job
    st.session_state.job_defined = job_defined
    st.session_state.cost_estimate_data = cost_estimate_data
    st.session_state.estimation_data_defined = estimation_data_defined
    st.session_state.all_cost_data = all_cost_data
    st.session_state.historical_data_defined = historical_data_defined
    st.session_state.date_range = date_range
    st.session_state.period_selected = period_selected
    st.session_state.reporting_month_data_defined = reporting_month_data_defined
    st.session_state.reporting_month_cost_data = reporting_month_cost_data
    st.session_state.forecast_end_date = forecast_end_date
    st.session_state.cost_forecast_settings = cost_forecast_settings
    st.session_state.cost_data_table = cost_data_table
    st.session_state.cost_forecast_settings_defined = cost_forecast_settings_defined 


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
if job_defined and not estimation_data_defined:
    # st.write(" Get estimation data for job")
    cost_estimate_data = get_cost_estimate_data(job)
    estimation_data_defined = True



"""  GET ALL HISTORICAL DATA  """
if estimation_data_defined and not historical_data_defined:
    # st.write(" Get all historical data for job")
    all_cost_data = get_all_cost_data(company, job)
    date_range = get_date_range(all_cost_data)
    historical_data_defined = True



"""  DEFINE THE REPORTING MONTH  """
if historical_data_defined:
    # st.write(" Defining the reporting month")
    # select_reporting_month(date_range)
    reporting_month = select_reporting_month(date_range)



"""  THE 'ACTUAL DATA' FOR REPORTING PERIOD. """
if reporting_month != "" and not cost_forecast_settings_defined:
    st.write(" Creating reporting month cost data")
    cost_by_fiscal_period = all_cost_data.copy()
    reporting_month_cost_data = create_cost_data_for_reporting_month(cost_estimate_data, cost_by_fiscal_period, date_range, reporting_month)
    reporting_month_data_defined = True



"""  THE FORECAST SETTINGS  """
if reporting_month_data_defined:
    if st.session_state.cost_forecast_settings_defined == False:
        st.write("Creating new forecast settings")
        forecast_end_date = select_forecast_end_date()
        cost_forecast_settings = get_cost_forecast_settings(cost_estimate_data, reporting_month, forecast_end_date)
    else:
        st.write("Recalculating cost forecast settings")
        my_cost_forecast_settings = recalculate_cost_forecast_settings(cost_forecast_settings, reporting_month, forecast_end_date)
    cost_forecast_settings_defined = True



"""  THE WHOLE RAW TABLE  -  Everything we need to know to calculate the grid table"""
if cost_forecast_settings_defined:
    st.write("Creating cost data table.")
    cost_data_table = create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, date_range[0], reporting_month, forecast_end_date)
    st.session_state.ready_for_grid = True

"""  THE WHOLE CALCULATED TABLE"""



"""  DISPLAY IN THE GRID  """
if st.session_state.ready_for_grid:
    grid_response = display_cost_in_grid(cost_data_table, date_range[0], reporting_month, forecast_end_date)

    # st.write('grid_response[data].iloc[:,13:]')
    # st.write(grid_response['data'].iloc[:,13:])

    # diff = grid_response['data'].compare(cost_data_table)
    # if len(diff) > 0:
    #     st.write(diff)
    #     if len(diff) > 1:
    #         st.write("TOO MANY DIFFERENCES")
    #     else:
    #         changed_column = diff.columns[0][0]
    #         new_value = diff[(changed_column,'self')].iloc[0]
    #         cost_item_changed = grid_response['data'][(grid_response['data'].index==diff.index[0])].cost_item.iloc[0]
    #         if changed_column=="item_start_date":
    #             new_value = datetime.strptime(new_value, "%d/%m/%Y")
    #             new_value = new_value.date()
    #         st.write("changed column: ", changed_column)
    #         st.write("new value: ", new_value)
    #         st.write("cost item changed: ", cost_item_changed)
    #         cost_forecast_settings.loc[cost_forecast_settings.cost_item == cost_item_changed, changed_column] = new_value
        
    # st.write("setting cost table = grid response")
    # cost_data_table = grid_response['data']


"""  DETECT USER CHANGES TO THE GRID  """



# st.write(cost_estimate_data)
# st.write('reporting_month_cost_data')
# st.write(reporting_month_cost_data.head(5))
# st.write('cost_forecast_settings')
# st.write(cost_forecast_settings.head(5))
# st.write('cost_data_table')
# st.write(cost_data_table)


st.button("rerun")

at_the_end()

# st.write('s.ss.cost_forecast_settings end')
# st.write(st.session_state.cost_forecast_settings)





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