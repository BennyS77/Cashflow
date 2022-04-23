from datetime import datetime
from operator import truediv
from urllib import response
import streamlit as st
# from st_aggrid import AgGrid
from my_config import page_config_and_session_state
from cashflow_functions import page_layout, get_cost_forecast_settings, display_cost_in_grid
from cashflow_functions import select_reporting_month, select_forecast_end_date, check_for_database_table
from cashflow_functions import create_cost_data_for_reporting_month, create_cost_data_table
from cashflow_functions import get_company, get_job, get_cost_estimate_data, get_all_cost_data, get_date_range
from cashflow_functions import get_whole_cost_table, user_login
from database_operations import read_table_from_database, write_table_to_database, drop_table, table_names
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

"""  """
page_config_and_session_state()
at_the_start()

page_layout()

"""  Login if needed  """
if not st.session_state.login_confirmed:
    user_login()

""" If logged in - """


ready_ph = st.sidebar.empty()
ready_ph.write("Not ready for grid:")

if st.session_state.login_confirmed:

    """  1.  THE COMPANY  """
    company, costs_for_company = get_company()


    """  2. THE JOB  """
    if company != "":
        job, costs_for_job = get_job(costs_for_company)


    """  TABLE NAME """
    table_name = ("report_data_"+company+job).lower()

    

    table_exists = None
    if job != '':
        # try:
        #     drop_table(table_name)
        # except:
        #     st.sidebar.write("Table didnt exist anyway")
        """  DOES THE DATABASE TABLE EXIST FOR THE JOB?  """
        table_exists = check_for_database_table(table_name)


    if table_exists:
        """ Do we want to read the database table everytime?? Yes for now"""
        whole_cost_table, first_cost_month, reporting_month_list, forecast_end_date = get_whole_cost_table(table_name)
        select_reporting_month(reporting_month_list)
        cost_data_table = whole_cost_table[whole_cost_table['reporting_month']==st.session_state.reporting_month]
        ready_ph.write("6. Ready for grid:")
        st.session_state.ready_for_grid = True


    if table_exists == False and job != '':
        """  GET ESTIMATION DATA  """
        cost_estimate_data = get_cost_estimate_data(job)


        """  GET ACTUAL DATA  """
        cost_data = get_all_cost_data(costs_for_job)
        date_range = get_date_range(cost_data)
        first_cost_month = date_range[0]

        # st.write(all_cost_data)

        """  DEFINE REPORTING MONTH  """
        select_reporting_month(date_range)


        """  DATA FOR THE REPORTING MONTH. """
        cost_by_fiscal_period = cost_data.copy()
        reporting_month_cost_data = create_cost_data_for_reporting_month(cost_estimate_data, cost_by_fiscal_period, date_range)

        # st.write(reporting_month_cost_data)

        """  THE FORECAST SETTINGS  """
        forecast_end_date = select_forecast_end_date()
        cost_forecast_settings = get_cost_forecast_settings(cost_estimate_data, reporting_month, forecast_end_date)


        if not st.session_state.ready_for_grid:
            """  THE TABLE DATA  -  Everything we need to know to calculate the grid table"""
            cost_data_table = create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, date_range[0], reporting_month, forecast_end_date)
            st.sidebar.write('Generated from current cost data')
            
            # st.write(cost_data_table)
            # write_table_to_database(cost_data_table, table_name)
            ready_ph.write("7. Ready for grid:")
            st.session_state.ready_for_grid = True



    """  DISPLAY IN THE GRID  """
    if st.session_state.ready_for_grid:

        grid_response = display_cost_in_grid(cost_data_table, first_cost_month, reporting_month, forecast_end_date)

    #     # st.write('grid_response[data].iloc[:,13:]')
        # st.write("grid_response['data'] that will be written to the database")
        st.write(grid_response['data'])
        
        #### Convert strings (as output from the grid) to Datetime/Timestamp before saving to the database.
        grid_response['data']['reporting_month'] = grid_response['data'].apply(lambda x: datetime.strptime(x.reporting_month,"%b %Y"), axis=1)
        grid_response['data']['item_start_date'] = grid_response['data'].apply(lambda x: datetime.strptime(x.item_start_date,"%d/%m/%Y"), axis=1)
        grid_response['data']['item_end_date'] = grid_response['data'].apply(lambda x: datetime.strptime(x.item_end_date,"%d/%m/%Y"), axis=1)
        st.write("grid_response['data'] after converting dates")
        st.write(grid_response['data'])

        st.sidebar.write("This is where we write to the database")
        write_table_to_database(grid_response['data'], table_name)
        ready_ph.write("8. Not ready for Grid!")
        st.session_state.ready_for_grid = False




        # whole_cost_table, first_cost_month, reporting_month_list, forecast_end_date = get_whole_cost_table(table_name)
        # st.write('whole_cost_table from database')
        # st.write(whole_cost_table)

    #     diff = grid_response['data'].compare(cost_data_table)
    #     if len(diff) > 0:
    #         st.write(diff)
    #         cost_data_table = grid_response['data']
    #         st.write('grid response being written to database')
    #         st.write(cost_data_table)
    #         write_table_to_database(cost_data_table, table_name)

    #         # changed_column = diff.columns[0][0]
    #         # new_value = diff[(changed_column,'self')].iloc[0]
    #         # cost_item_changed = grid_response['data'][(grid_response['data'].index==diff.index[0])].cost_item.iloc[0]
    #         # if changed_column=="item_start_date":
    #         #     new_value = datetime.strptime(new_value, "%d/%m/%Y")
    #         #     new_value = new_value.date()
    #         # st.write("changed column: ", changed_column)
    #         # st.write("new value: ", new_value)
    #         # st.write("cost item changed: ", cost_item_changed)
    #         # cost_data_table.loc[cost_data_table.cost_item == cost_item_changed, changed_column] = new_value
        
    #     # st.write("setting cost table = grid response")
    #     # cost_data_table = grid_response['data']


    # """  DETECT USER CHANGES TO THE GRID  """


    # at_the_end()
    # st.button("press")
    # # st.write(st.session_state.cost_data_table.iloc[:5,2:])