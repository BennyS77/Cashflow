import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from st_aggrid import AgGrid
from dateutil.relativedelta import relativedelta
from visuals import gantt_chart, bar_chart
from my_config import pageConfig, setSessionData, setLogIn, page_layout
from cost_data import getCompanyAndJobList, getJobCostByFiscalPeriod, getEACdata, getJobList, createForecastDetails
from cost_data import filterFormatData,  update_reporting_month, forecast_calcs, create_forecast_data_table
from cost_data import calculate_pinned_row_data, get_forecast_data_for_reporting_month, calculate_cost_data_for_the_grid
from cost_data import create_reporting_month_data
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
from database_operations import writeDetailsToDatabase, readDetailsFromDatabase, drop_table

pageConfig()
setSessionData()
# page_layout()
st.session_state.ready_for_grid = False
st.markdown("## Cost Forecast")




creds = setLogIn()

msg_ph = st.sidebar.empty()

if st.session_state.login_confirmed:
    # msg_ph.write(  """  Credentials confirmed. Select a company:  """  )
    company_list, companies_and_jobs = getCompanyAndJobList(creds)
    # st.sidebar.selectbox("Company:", company_list, index = len(company_list)-1, key='company')
    st.session_state.company = 'G01'; st.sidebar.write('Company: ', st.session_state.company)



if st.session_state.company:
    # msg_ph.write(  """   Company selected. Choose a Job:  """  )
    job_list = getJobList(st.session_state.company, companies_and_jobs)
    # st.sidebar.selectbox("Job:", job_list, index = len(job_list)-1, key = 'job' )
    # st.sidebar.selectbox("Job:", ['PD140479'],  key = 'job' )
    st.session_state.job = 'PD140479'; st.sidebar.write('Job: ', st.session_state.job)



if st.session_state.job:
    # drop_table(('forecast_details_'+st.session_state.company+st.session_state.job).lower())
    # msg_ph.write(  """   Job selected. Get all 'Actual' cost data for job and then choose Reporting Month: """ )
    cost_by_calendar_month, date_range = filterFormatData(st.session_state.company, st.session_state.job, creds)
    eac_data = getEACdata()
    st.sidebar.selectbox(
                "Reporting month:",
                date_range,
                index = (len(date_range)-1),
                format_func=lambda x: x.strftime('%b %Y') if x!="" else x,
                key="reporting_month",
                on_change = update_reporting_month
                )



if st.session_state.reporting_month:
    # msg_ph.write("""   Reporting month has been selected.  """)
    try:
        # """  Try getting Forecast Data table for the job from database table: """
        all_forecast_data = readDetailsFromDatabase(('forecast_details_'+st.session_state.company+st.session_state.job).lower())
    except:
        # """  'Forecast Data' table does not exist. Create new table:  """
        # """  After writing it to the database, on the next rerun it wont go through here  """  
        st.sidebar.date_input(
            "Forecast end date for new Forecast Table:",
            (datetime.today() + relativedelta(months=6)).date(),
            key = 'forecast_end_date',
            # kwargs = dict(the_details = all_forecast_data),
            on_change = create_forecast_data_table
        )
    
    # """  Extract Reporting Month data from the Forecast Data  """
    forecast_data_for_reporting_month = all_forecast_data.loc[all_forecast_data['reporting_month'] == st.session_state.reporting_month]
    if len(forecast_data_for_reporting_month)>0:
        # """ If Forecast Data exists for month exists, get the Forecast End Date """
        st.session_state.forecast_end_date = forecast_data_for_reporting_month['forecast_end_date'].iloc[0]
        st.session_state.ready_for_grid = True
    else:
        # """ If Forecast Data = Empty, create default data for the month and add it to the database table  """
        st.sidebar.date_input(
            "Choose Forecast End Date for the new Reporting Month:",
            (datetime.today() + relativedelta(months=6)).date(),
            key = 'forecast_end_date',
            kwargs = dict(the_details = all_forecast_data),
            on_change = create_reporting_month_data
        )






if st.session_state.ready_for_grid:
    grid_cost_data, pinned_row_data = calculate_cost_data_for_the_grid(cost_by_calendar_month, forecast_data_for_reporting_month, date_range)
    actual_children = configActualChildren(date_range[0], st.session_state.reporting_month)
    forecast_children = configForecastChildren(st.session_state.reporting_month, st.session_state.forecast_end_date)
    gridOptions, custom_css = configureGridOptions(actual_children, forecast_children, pinned_row_data)
    # st.write(grid_cost_data)
    grid_cost_data['item_start_date']=grid_cost_data['item_start_date'].apply(lambda x: x.strftime("%d/%m/%Y"))
    grid_cost_data['item_end_date']=grid_cost_data['item_end_date'].apply(lambda x: x.strftime("%d/%m/%Y"))



    ## Chart at the top ##
    # fig = gantt_chart()
    fig = bar_chart()
    st.plotly_chart(fig)

    grid_response = AgGrid(
      dataframe = grid_cost_data,
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
