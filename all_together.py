import streamlit as st
from datetime import datetime
from st_aggrid import AgGrid
import random
import pandas as pd
import numpy as np
from visuals import bar_chart
from dateutil.relativedelta import relativedelta
from my_config import page_config_and_session_state
from cashflow_functions import user_login, get_company, check_for_database_table, get_whole_cost_table, get_odata_list, get_cost_forecast_settings, display_cost_in_grid
from cashflow_functions import fetch_Odata, get_cost_estimate_data, get_all_cost_data ,get_date_range, create_cost_data_for_reporting_month, create_cost_data_table, page_layout
from database_operations import read_table_from_database, update_table, write_table_to_database
from aggrid_functions_cost import config_actual_cost_children, config_forecast_cost_children, configure_cost_grid_options
# from cost_data import calculate_pinned_row_data

def get_company_list():
    # st.session_state.company_list = ['AA','BB',""]
    cost_by_fiscal_period = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
    st.session_state.company_list = cost_by_fiscal_period['Company_Code'].drop_duplicates().tolist()
    st.session_state.company_list.append("")
    return

def company_selectbox():
    def company_change():
        st.session_state.job = ""
        st.session_state.job_list = []
        st.session_state.ready_for_grid = False
        return
    st.sidebar.selectbox(label = "Choose Company:",
                    index = (len(st.session_state.company_list)-1), 
                    options = st.session_state.company_list,
                    key = "company",
                    on_change = company_change
                    )
    return

def get_job_list():
    # st.session_state.job_list = ['A1101','B-202',""]
    cost_by_fiscal_period = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
    job_data = cost_by_fiscal_period[cost_by_fiscal_period['Company_Code']==st.session_state.company]
    st.session_state.job_list = job_data['Job_Number'].drop_duplicates().tolist()
    st.session_state.job_list.append("")
    # st.write(st.session_state.job_list)
    return

def job_selectbox():
    def job_change():
        st.session_state.grid_key += 1
        st.session_state.show_reporting_month = False
        st.session_state.show_forecast_end_date = False
        st.session_state.reporting_month = ""
        st.session_state.forecast_end_date = []
        st.session_state.ready_for_grid = False
        return
    if st.session_state.job_list == []:
        get_job_list()
    st.sidebar.selectbox(label = "Choose Job:",
                        # index = (len(st.session_state.job_list)-1), 
                        options = st.session_state.job_list,
                        key = 'job',
                        on_change = job_change
                        )
    return

def report_month_selection():
    def change_report_month():
        st.session_state.grid_key += 1
        st.session_state.ready_for_grid = False
        return
    options_list = st.session_state.reporting_month_list + [""]
    st.sidebar.selectbox(label = "Reporting Month:",
                        index = (len(st.session_state.reporting_month_list)), 
                        options = options_list,
                        key = 'reporting_month',
                        on_change = change_report_month
                        )
    return

def get_forecast_end_date():
    def end_date_change():
        # st.session_state.show_forecast_end_date = True
        return
    st.sidebar.date_input(label="Forecast End Date:",
                        # value=pd.Period(datetime.today() + relativedelta(months=6), freq='M').end_time,
                        on_change = end_date_change,
                        key = 'forecast_end_date'
                        )
    
    return

def get_first_cost_month():
    cols = list(st.session_state.grid_cost_data.columns.values)
    date_cols = []
    for column in cols:
        try:
            datetime.strptime(column,"%Y-%m")
            date_cols.append(datetime.strptime(column,"%Y-%m"))
        except:
            pass
    return min(date_cols)

def create_job_cost_data_table():
    cost_estimate_data = get_cost_estimate_data(st.session_state.job)
    cost_data = get_all_cost_data()
    date_range = get_date_range(cost_data)
    reporting_month = pd.Period(datetime.today()+relativedelta(months=-1), freq='M').start_time ## Creates a Timestamp
    reporting_month_cost_data = create_cost_data_for_reporting_month(cost_estimate_data, cost_data, date_range, reporting_month)
    cost_forecast_settings = get_cost_forecast_settings(cost_estimate_data, reporting_month, st.session_state.forecast_end_date)
    cost_data_table = create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, date_range[0], reporting_month, st.session_state.forecast_end_date)
    return cost_data_table


page_config_and_session_state()
page_layout()

testing = True

if testing:
    st.session_state.session_number += 1
    st.sidebar.markdown(f"#### Session Re-run: {st.session_state.session_number}")
    st.session_state.credentials = {"username":'319006\JP.API', "password":'tYzxU2fQuJvrVSgJ'}
    st.session_state.login_confirmed = True
    st.session_state.company_list = ['NS', ""]
    st.session_state.company = 'NS'
    st.session_state.job = 'NSG21-010'
    if 'reporting_month' not in st.session_state:
        st.session_state.reporting_month = ''
    

col1,col2,col3,col4 = st.columns([1,1,1,1])
with col1:
    start_date = st.empty()
    start_date.markdown("Start Date:")
with col2:
    end_date = st.empty()
    end_date.markdown("End Date:")
with col3:
    margin = st.empty()
    margin.markdown("Margin:")
with col4:
    project_manager = st.empty()
    project_manager.markdown("Project Manager:")



if st.session_state.login_confirmed:
    """
    ...LOGGED-IN -  SELECT COMPANY AND JOB...
    """
    if st.session_state.company_list == []:
        get_company_list()
    company_selectbox()
    if st.session_state.company != "":
        job_selectbox()
    table_name = ("report_data_"+st.session_state.company+st.session_state.job).lower()
    if st.session_state.job != "" and not st.session_state.ready_for_grid:
        """
        ...NOT READY FOR GRID - CHECK FOR DATABASE TABLE...
        """
        job_data_exists = check_for_database_table(table_name)
        if not job_data_exists:
            """
            ...JOB DATA 'DOES-NOT' EXIST IN THE DATABASE
            """
            st.session_state.show_forecast_end_date = True
            if st.session_state.forecast_end_date:
                """
                ...HAVE FORECAST END DATE - CREATE NEW JOB TABLE IN DATABASE FOR CURRENT REPORTING PERIOD...
                """
                st.sidebar.write(f"forecast end date: {st.session_state.forecast_end_date}")
                cost_data_table = create_job_cost_data_table()
                st.write(cost_data_table)
                write_table_to_database(cost_data_table, table_name)
                # st.experimental_rerun()
                st.sidebar.button("rerun")
        else:
            """
            ...JOB DATA 'DOES' EXIST IN THE DATABASE...
            """
            st.session_state.job_data_table = read_table_from_database(table_name)
            st.session_state.reporting_month_list = st.session_state.job_data_table['reporting_month'].drop_duplicates().tolist()
            st.session_state.show_reporting_month = True
            if st.session_state.reporting_month != "":
                """
                ...REPORTING MONTH SELECTED...
                """
                st.session_state.grid_cost_data = st.session_state.job_data_table[st.session_state.job_data_table['reporting_month']==st.session_state.reporting_month]
                st.session_state.grid_cost_data['item_start_date']=st.session_state.grid_cost_data.apply(lambda x: x['item_start_date'].strftime("%d/%m/%Y"), axis=1)
                st.session_state.grid_cost_data['item_end_date'] = st.session_state.grid_cost_data.apply(lambda x: x['item_end_date'].strftime("%d/%m/%Y"), axis=1)
                st.session_state.ready_for_grid = True

                
            else:
                pass
                # st.sidebar.write("Select Reporting Month to continue.")
        
    else:
        pass
        # st.write("Need to select Job:")

    if st.session_state.show_forecast_end_date:
        get_forecast_end_date()


    if st.session_state.show_reporting_month:
        report_month_selection()



    """
    ....GENERATE GRID....
    """
    if st.session_state.ready_for_grid:


        """
        ...Calculate Pinned Row Data...
        """
        st.session_state.grid_cost_data['total_amount'] = st.session_state.grid_cost_data.apply(lambda x: x.total*x.EAC/100, axis=1)
        pinned_row_dict={
            "autoGroup":"Total Costs:",
            "EAC":st.session_state.grid_cost_data['EAC'].sum(),
            "ACTD_percent":st.session_state.grid_cost_data['total_amount'].sum()/st.session_state.grid_cost_data['EAC'].sum()*100,
            "ACTD_amount":st.session_state.grid_cost_data['total_amount'].sum(),
            "ETC_percent":(1-(st.session_state.grid_cost_data['total_amount'].sum()/st.session_state.grid_cost_data['EAC'].sum()))*100,
            "ETC_amount":st.session_state.grid_cost_data['EAC'].sum() - st.session_state.grid_cost_data['total_amount'].sum()
        }

        first_cost_month = get_first_cost_month()
        forecast_end_date = st.session_state.grid_cost_data['item_end_date'].max()
        last_actual_month = st.session_state.reporting_month+relativedelta(months=1)
        my_range = pd.date_range(start=first_cost_month, end=last_actual_month, freq='M').tolist()
        for i, item in enumerate(my_range):
            coolness = st.session_state.grid_cost_data.apply(lambda x: x[item.strftime('%Y-%m')]*x.EAC, axis=1).sum()
            pinned_row_dict.update({item.strftime('%Y-%m')+'-c':coolness/st.session_state.grid_cost_data.EAC.sum()*100})
            pinned_row_dict.update({item.strftime('%Y-%m')+'-$':coolness})

        first_forecast_month = st.session_state.reporting_month+relativedelta(months=1)
        cool_range = pd.period_range(first_forecast_month, forecast_end_date, freq='M').tolist()
        # forecast_date_range = pd.date_range(start = first_forecast_month, end = last_forecast_month, freq='M').tolist()
        for i, item in enumerate(cool_range):
            if i == 0:
                coolness = st.session_state.grid_cost_data.apply(
                        lambda x: (x[item.strftime('%Y-%m')+'-cF']-x['total'])/100*x.EAC, axis=1).sum()
                pinned_row_dict.update({item.strftime('%Y-%m')+'-cF':coolness/st.session_state.grid_cost_data.EAC.sum()*100})
                pinned_row_dict.update({item.strftime('%Y-%m')+'m$':coolness})
            else:
                coolness = st.session_state.grid_cost_data.apply(
                        lambda x: (x[item.strftime('%Y-%m')+'-cF'] - x[cool_range[i-1].strftime('%Y-%m')+'-cF'] ) /100 *x.EAC, axis=1).sum()
                pinned_row_dict.update({item.strftime('%Y-%m')+'-cF':coolness/st.session_state.grid_cost_data.EAC.sum()*100})
                pinned_row_dict.update({item.strftime('%Y-%m')+'m$':coolness})


        """
        ...Calculate data for the graph...
        """
        def search(my_dict, search_string):
            key_list = []
            value_list = []
            for key, value in my_dict.items():
                if search_string in key:
                    key_list.append(key[:7])
                    value_list.append(value)
            return key_list, value_list
        
        all_months, all_cost_amounts = search(pinned_row_dict, '$')
        number_of_months = len(all_months)

        """ Generate some dummy revenue data"""
        # if len(st.session_state.revenue_amounts)==0:
        st.session_state.revenue_amounts = [item *  (0.8 + (random.random()*0.7)) for item in all_cost_amounts]

        cashflow =[int(item1 - item2) for (item1, item2) in zip(st.session_state.revenue_amounts,all_cost_amounts)]
        cum_cashflow = np.cumsum(cashflow)

        fig = bar_chart(all_months, all_cost_amounts, st.session_state.revenue_amounts, cum_cashflow, number_of_months)
        
        # st.write('all_months')
        # st.write(all_months)
        # st.write('all_cost_amounts')
        # st.write(all_cost_amounts)
        # st.write('st.session_state.revenue_amounts')
        # st.write(st.session_state.revenue_amounts)
        # st.write('cashflow')
        # st.write(cashflow)
        # st.write('cum_cashflow')
        # st.sidebar.write(cum_cashflow)


        """
        ...Display cashflow figure at the top...
        """
        config = {'displayModeBar':False}
        st.plotly_chart(fig, config=config, use_container_width=True)


        st.session_state.grid_cost_data['total_column']='TOTAL:'  ### For grouping purposes in the grid.

        actual_children = config_actual_cost_children(first_cost_month, st.session_state.reporting_month)
        forecast_children = config_forecast_cost_children(st.session_state.reporting_month+relativedelta(months=1), forecast_end_date)
        grid_options = configure_cost_grid_options(actual_children, forecast_children, [pinned_row_dict])
        # st.write(st.session_state.grid_cost_data)
        # st.write(pinned_row_dict)

        col1, col2 = st.columns([1,1])
        with col1:
            st.markdown("## COST")
        with col2:
            st.markdown("## REVENUE")

        grid_response = AgGrid(
                dataframe = st.session_state.grid_cost_data,
                gridOptions = grid_options, 
                height = 650,
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                key = st.session_state.grid_key,
                reload_data=False,  
                # reload_data=True,  
                data_return_mode='AS_INPUT',
                update_mode='MODEL_CHANGED',
                allow_unsafe_jscode=True,
                theme="light"
        )

        """
        ....DETECT CHANGES TO THE GRID....
        """
        diff = grid_response['data'].compare(st.session_state.grid_cost_data)
        if len(diff) > 0:
            st.write(diff) ## Dataframe
            dict_of_changes = {}
            for item in diff.columns:
                if 'self' in item:
                    dict_of_changes.update({item[0]:diff[item].iloc[0]})
            where_column = 'cost_item'
            cost_item_changed = grid_response['data'][(grid_response['data'].index==diff.index[0])][where_column].iloc[0]
            where_column2 = 'reporting_month'
            value2 = "'"+st.session_state.reporting_month.strftime("%Y-%m-%dT%H:%M:%S")+"'"
            for key, value in dict_of_changes.items():
                st.session_state.grid_cost_data.loc[st.session_state.grid_cost_data[where_column] == cost_item_changed, key] = value
                column = '"'+key+'"'
                if key == 'forecast_method':
                    value="'"+value+"'"
                elif key == 'item_start_date' or key == 'item_end_date':
                    value = datetime.strptime(value, "%d/%m/%Y")
                    value="'"+value.strftime("%Y-%m-%dT%H:%M:%S")+"'"
                update_table(table_name, column, str(value), where_column, "'"+cost_item_changed+"'", where_column2, value2)
            st.experimental_rerun()
            # st.write(st.session_state.grid_cost_data)   



else:
    user_login()


if st.sidebar.button("Clear all"):
    st.experimental_memo.clear()


### LOOK AT: 'value cache', 'column filters'


# current_report_period = pd.Period(datetime.today()+relativedelta(months=-1), freq='M').start_time
                # # if st.session_state.job_data_table['reporting_month'].max() == current_report_period:
                # if st.session_state.reporting_month == current_report_period:
                #     """
                #     ...SELECTED MONTH IS CURRENT REPORTING MONTH - GIVE OPTION TO REFRESH DATA
                #     """
                #     refresh_data = st.sidebar.button("Refresh data")
                #     if refresh_data:
                #         '''
                #         ...USER HAS SELECTED TO REFRESH REPORT DATA...
                #         '''
                #         st.sidebar.write("Oops, not working yet. Try again soon :)")
                #     else: 
                #         """
                #         ...USE EXISTING REPORT DATA - DECLARE REPORT DATA READY FOR GRID...
                #          """


# else:
                #     """
                #     ...SELECTED MONTH IS .NOT. CURRENT REPORTING MONTH - GIVE OPTION TO CREATE REPORTING MONTH DATA
                #     """
                #     create_new = st.sidebar.button("Create New:")
                #     forecast_end_date = st.session_state.job_data_table['item_end_date'].max()
                #     if create_new:
                #         """
                #         ...CREATE REPORT DATA FOR CURRENT REPORTING MONTH...
                #         """
                #         cost_estimate_data = get_cost_estimate_data(st.session_state.job)
                #         cost_data = get_all_cost_data()
                #         date_range = get_date_range(cost_data)
                #         first_cost_month = date_range[0]
                #         reporting_month = pd.Period(datetime.today()+relativedelta(months=-1), freq='M').start_time
                #         reporting_month_cost_data = create_cost_data_for_reporting_month(cost_estimate_data, cost_data, date_range, reporting_month)
                #         cost_forecast_settings = get_cost_forecast_settings(cost_estimate_data, reporting_month, forecast_end_date)
                #         cost_data_table = create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, date_range[0], reporting_month, forecast_end_date)
                #         table_for_database = pd.concat([st.session_state.job_data_table,cost_data_table])
                #         write_table_to_database(table_for_database, table_name)
                #         st.sidebar.write("RERUN SCRIPT AFTER CREATING REPORT DATA FOR CURRENT REPORTING MONTH")
                #         st.sidebar.button("rerun")
                #     else:
                #         """
                #         ...USE PREVIOUS REPORTING MONTH DATA IN THE GRID...
                #         """
                #         st.session_state.grid_cost_data = st.session_state.job_data_table[st.session_state.job_data_table['reporting_month']==st.session_state.reporting_month]
                #         st.session_state.grid_cost_data['item_start_date']=st.session_state.grid_cost_data.apply(lambda x: x['item_start_date'].strftime("%d/%m/%Y"), axis=1)
                #         st.session_state.grid_cost_data['item_end_date'] = st.session_state.grid_cost_data.apply(lambda x: x['item_end_date'].strftime("%d/%m/%Y"), axis=1)
                #         st.sidebar.write("Ready for the grid using historical report data.")
                #         st.session_state.ready_for_grid = True



# st.sidebar.markdown(f"#### Reporting Month by end: {st.session_state.reporting_month}")

# st.button("rerun")





##### Suitable test jobs
# Not much in Reitsma
# Colibrico - not BE-21-47, BAL-22-05, BAL-21-35, BAL-21-02
#           - suitable ''BAL-21-32'', BAL-21-30

# PHASE - not C351, C354, R419
#       - suitable LA007

# Akura - not 846, 766, T1012D, 265, V974

# Ecowise - not H00710, H760,

# Neverstop - suitable 'NSG21-010', NSG21-014,