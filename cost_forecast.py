import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from st_aggrid import AgGrid
from dateutil.relativedelta import relativedelta
from my_config import pageConfig, setSessionData, setLogIn
from cost_data import getCompanyAndJobList, getJobCostByFiscalPeriod, getEACdata, getJobList, createForecastDetails
from cost_data import filterFormatData, calc_cost_per_month_and_ACTD, merge_eac_and_calc_percent, forecast_calcs
from cost_data import calculate_pinned_row_data
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
from database_operations import writeDetailsToDatabase, readDetailsFromDatabase

def update_grid_key():
    """ Change grid key so that the grid re-initialises after changing the date"""
    st.session_state.grid_key = st.session_state.grid_key + 1

## 1
pageConfig()

## 2
setSessionData()

## 3
creds, submit_button = setLogIn()
# if submit_button:
st.session_state.submitted = True

## 4
# if st.session_state.submitted:
company_list, companies_and_jobs = getCompanyAndJobList(creds)
# company = st.sidebar.selectbox("Company:", company_list, index = len(company_list)-1)
company = st.sidebar.selectbox("Company:", ['G01'])

## 5
# try:
if company:
    job_list = getJobList(company, companies_and_jobs)
    # job = st.sidebar.selectbox("Job:", job_list, index = len(job_list)-1 )
    job = st.sidebar.selectbox("Job:",['PD140479'])
# except: 
#     st.write("Log in to retrieve data")

## 6
# try:
if job:
    all_jobs_cost_by_fiscal_period = getJobCostByFiscalPeriod(creds)
    cost_by_fiscal_period, date_range = filterFormatData(company, job, all_jobs_cost_by_fiscal_period)
    
    ## 7
    index = date_range.index(pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1))
    reporting_month = st.sidebar.selectbox(
                "Reporting month:",
                date_range,
                index = index,
                format_func=lambda x: x.strftime('%b %Y'),
                # key="reportingmonth",
                # on_change = report_change
                )
    eac_data = getEACdata()    

    try:
        forecast_details = readDetailsFromDatabase(('forecast_details_'+company+job).lower())
        # st.write('Forecast_details table exists.')
        st.session_state.forecast_table_exists = True
    except:
        st.write('Forecast_details table not available. Generating...')
        forecast_details = createForecastDetails(eac_data.cost_item, reporting_month, st.session_state.forecast_end_date)
        writeDetailsToDatabase(forecast_details, ('forecast_details_'+company+job).lower())

    forecast_data_for_reporting_month = forecast_details.loc[forecast_details['reporting_month'] == reporting_month]
    # st.write(forecast_data_for_reporting_month)

    if len(forecast_data_for_reporting_month)>0:
        # st.write("Data for Reporting Month exists.")
        forecast_end_date = forecast_data_for_reporting_month['forecast_end_date'].iloc[0]
        st.session_state.reportingmonth_data_exists = True
    else:
        st.write("Data for Reporting Month not available")
        forecast_end_date = st.sidebar.date_input(
            "forecast end date",
            (datetime.today() + relativedelta(months=6)).date(),
            # on_change = report_change
        )
    ### Will need to syse placeholdker fpor this
    # forecast_end_date = st.sidebar.date_input(
    #         "forecast end date",
    #         forecast_end_date,
    #         # on_change = report_change
    #     )

    # st.write(f"Reporting month: {reporting_month}")
    # st.write(f"Forecast end Date: {forecast_end_date}")

    ## 9
    cost_with_ACTD = calc_cost_per_month_and_ACTD(cost_by_fiscal_period, date_range[0], reporting_month)
    ### The order/details of the merge needs to be updated 
    cost_data = merge_eac_and_calc_percent(cost_with_ACTD, eac_data, date_range[0], reporting_month)

    ## 13  (I know right, something's weird with the numbering...)
    cost_display_data = forecast_calcs(cost_data, forecast_data_for_reporting_month)

    pinned_row_data = calculate_pinned_row_data(cost_display_data, date_range, reporting_month, forecast_end_date)
    actual_children = configActualChildren(date_range[0], reporting_month)
    forecast_children = configForecastChildren(reporting_month, forecast_end_date)
    gridOptions, custom_css = configureGridOptions(actual_children, forecast_children, pinned_row_data)

    ##### GANTT CHART ######

    gantt_df = pd.DataFrame([
        dict(Cost_Item="Cost Item 110", Start='2022-01-01', Finish='2022-02-28', complete=50),
        dict(Cost_Item="Cost Item 120", Start='2022-02-01', Finish='2022-04-15', complete=35),
        dict(Cost_Item="Cost Item 230", Start='2022-01-20', Finish='2022-05-3', complete=70),
        dict(Cost_Item="Cost Item 250", Start='2022-01-01', Finish='2022-03-15', complete=20),
        dict(Cost_Item="Cost Item 325", Start='2022-02-01', Finish='2022-06-15', complete=45),
        dict(Cost_Item="Cost Item 410", Start='2022-01-20', Finish='2022-05-3', complete=90)
    ])

    fig = px.timeline(gantt_df, x_start="Start", x_end="Finish", y="Cost_Item", color='complete')
    fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
    fig.update_layout(
            width=1600,
            height=400,
            margin=dict(
                l=1,
                r=0,
                b=0,
                t=1
                )
            )
    st.plotly_chart(fig)


    grid_response = AgGrid(
      dataframe = cost_display_data,
      custom_css = custom_css,
      gridOptions = gridOptions, 
      height = 700,
      enable_enterprise_modules=True,
      fit_columns_on_grid_load=False,
      key = st.session_state.grid_key,   #- set a key to stop the grid reinitialising when the dataframe changes
    #   reload_data=True,  
      reload_data=False,  
      data_return_mode='AS_INPUT',
    #   data_return_mode='FILTERED',
      update_mode='VALUE_CHANGED',   ## default
    #   update_mode='MODEL_CHANGED',
      allow_unsafe_jscode=True,
      theme="light"  
        # 'streamlit'
        # "light" - balham-light
        # "dark" - balham-dark
        # "blue" - blue
        # "fresh" - fresh
        # "material" - material
      )
##7 





# try:
# except:
#     st.write("no data yet")





    # if company:

    #     ## 4
    #     job_list = getJobList(company, companies_and_jobs)
    #     # job = st.sidebar.selectbox("Job:", job_list, index = len(job_list)-1 )
    #     job = st.sidebar.selectbox("Job:",['PD140479'])

    #     if job:

    #         ## 5 
    #         all_jobs_cost_by_fiscal_period = getJobCostByFiscalPeriod(creds)

    #         ## 6 
    #         eac_data = getEACdata()

    #         cost_by_fiscal_period, date_range = filterFormatData(company, job, all_jobs_cost_by_fiscal_period)
    #         index = date_range.index(pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1))

    #         st.write()

    #         def form_callback():
    #             """ Figure out what to do here"""
    #         #     forecast_details['forecast_end_date'] = st.session_state.forecastenddate
    #             # forecast_details['reporting_month'] = st.session_state.reportingmonth
    #         #     writeDetailsToDatabase(forecast_details, ('forecast_details_'+selected_company+selected_job).lower())

    #         with st.sidebar.form(key='my_form'):
    #             forecast_end_date = st.sidebar.date_input(
    #                 "Forecast end date",
    #                 (datetime.today() + relativedelta(months=6)).date(),
    #                 on_change = report_change
    #                 )
    #             reporting_month = st.sidebar.selectbox(
    #                 "Reporting month:",
    #                 date_range,
    #                 index = index,
    #                 format_func=lambda x: x.strftime('%b %Y'),
    #                 key="reportingmonth",
    #                 on_change = report_change
    #                 )
    #             submit = st.form_submit_button(label='Submit', on_click = form_callback)
            
    #         cost_with_ACTD = calc_cost_per_month_and_ACTD(cost_by_fiscal_period, date_range[0], reporting_month)
            
    #         cost_data = merge_eac_and_calc_percent(cost_with_ACTD, eac_data, date_range[0], reporting_month)
            
    #         if st.session_state.table_1_exists == False:
    #             # st.write(" !! New Job !!  Database table does not exist. Creating....")
    #             st.session_state.table_1 = createForecastDetails(eac_data.cost_item, reporting_month, forecast_end_date)
    #             st.session_state.table_1_exists = True
            
    #         forecast_data_for_reporting_month = st.session_state.table_1.loc[st.session_state.table_1['reporting_month'] == reporting_month.date()]
            
    #         cost_display_data = forecast_calcs(cost_data, forecast_data_for_reporting_month)
    #         # st.write(cost_display_data)


    #         rowDataDict={"autoGroup":"Total Costs:","EAC":cost_display_data['EAC'].sum(),"ACTD":cost_display_data['ACTD'].sum(),"ETC":cost_display_data['ETC'].sum()}

    #         my_range = pd.date_range(start=date_range[0], end=reporting_month, freq='M').tolist()

    #         for i, item in enumerate(my_range):
    #             # st.write(item)
    #             rowDataDict.update({item.strftime('%b_%y')+'_$':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum())})
    #             rowDataDict.update({item.strftime('%b_%y')+'_%':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum()/cost_display_data['EAC'].sum())})

    #         forecast_date_range = pd.date_range(start = reporting_month+relativedelta(months=1), end = forecast_end_date+relativedelta(months=1), freq='M').tolist()
    #         for i, item in enumerate(forecast_date_range):
    #             # st.write(item)
    #             rowDataDict.update({item.strftime('%b_%y')+'_F$':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum())})
    #             rowDataDict.update({item.strftime('%b_%y')+'_F%':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum()/cost_display_data['EAC'].sum())})

    #         pinnedRowData=[rowDataDict]



    #         actual_children = configActualChildren(date_range[0], reporting_month)
    #         forecast_children = configForecastChildren(reporting_month, forecast_end_date)
    #         gridOptions, custom_css = configureGridOptions(actual_children, forecast_children, pinnedRowData)

    #         grid_response = AgGrid(
    #             dataframe = cost_display_data,
    #             custom_css = custom_css,
    #             gridOptions = gridOptions, 
    #             height = 600,
    #             enable_enterprise_modules=True,
    #             fit_columns_on_grid_load=False,
    #             key = st.session_state.grid_key,   #- set a key to stop the grid reinitialising on reruns
    #             #   reload_data=True,  
    #             reload_data=False,  
    #             data_return_mode='AS_INPUT',
    #             #   data_return_mode='FILTERED',
    #             update_mode='VALUE_CHANGED',   ## default
    #             #   update_mode='MODEL_CHANGED',
    #             allow_unsafe_jscode=True,
    #             theme="light"  
    #                 # 'streamlit'
    #                 # "light" - balham-light
    #                 # "dark" - balham-dark
    #                 # "blue" - blue
    #                 # "fresh" - fresh
    #                 # "material" - material
    #             )











### Original original stuff

            ## 7
            # forecast_details = createForecastDetails(eac_data.costitem)
            ## 8
            # writeDetailsToDatabase(forecast_details, ('forecast_details_'+selected_company+selected_job).lower())

            ## 8b
            # forecast_details = readDetailsFromDatabase(('forecast_details_'+selected_company+selected_job).lower())

            ## 9
            # cost_data, date_range = filterFormatData(selected_company, selected_job, job_cost_by_fiscal_period)
            # index = date_range.index(forecast_details.reporting_month[0])

            # def form_callback():
            #     forecast_details['forecast_end_date'] = st.session_state.forecastenddate
            #     forecast_details['reporting_month'] = st.session_state.reportingmonth
            #     writeDetailsToDatabase(forecast_details, ('forecast_details_'+selected_company+selected_job).lower())

            # with st.sidebar.form(key='my_form'):
            #     st.date_input("Forecast end date:", forecast_details.forecast_end_date[0], key="forecastenddate")
            #     st.selectbox("Reporting month:", date_range, index = index, format_func=lambda x: x.strftime('%b %Y'), key="reportingmonth")
            #     submit = st.form_submit_button(label='Submit', on_click = form_callback)
