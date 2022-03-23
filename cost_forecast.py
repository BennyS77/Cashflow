import streamlit as st
from datetime import datetime
from my_config import pageConfig, setSessionData, setLogIn
from cost_data import getCompanyAndJobList, getJobCostByFiscalPeriod, getEACdata, getJobList, createForecastDetails
from cost_data import filterFormatData
from database_operations import writeDetailsToDatabase, readDetailsFromDatabase

pageConfig()

setSessionData()



## 1
creds, submit_button = setLogIn()
# if submit_button:
st.session_state.submitted = True



if st.session_state.submitted:

    ## 2
    company_list, companies_and_jobs = getCompanyAndJobList(creds)

    ## 3 
    # selected_company = st.sidebar.selectbox("Company:", company_list, index = len(company_list)-1)
    selected_company = st.sidebar.selectbox("Company:", ['G01'])

    if selected_company:

        ## 4
        job_list = getJobList(selected_company, companies_and_jobs)
        # selected_job = st.sidebar.selectbox("Job:", job_list, index = len(job_list)-1 )
        selected_job = st.sidebar.selectbox("Job:",['PD140479'])

        if selected_job:

            ## 5 
            job_cost_by_fiscal_period = getJobCostByFiscalPeriod(creds)

            ## 6 
            eac_data = getEACdata()

            ## 7
            # forecast_details = createForecastDetails(eac_data.costitem)
            ## 8
            # writeDetailsToDatabase(forecast_details, ('forecast_details_'+selected_company+selected_job).lower())

            ## 8b
            forecast_details = readDetailsFromDatabase(('forecast_details_'+selected_company+selected_job).lower())

            ## 9
            cost_data, date_range = filterFormatData(selected_company, selected_job, job_cost_by_fiscal_period)
            index = date_range.index(forecast_details.reporting_month[0])

            def form_callback():
                forecast_details['forecast_end_date'] = st.session_state.forecastenddate
                forecast_details['reporting_month'] = st.session_state.reportingmonth
                writeDetailsToDatabase(forecast_details, ('forecast_details_'+selected_company+selected_job).lower())

            with st.sidebar.form(key='my_form'):
                st.date_input("Forecast end date:", forecast_details.forecast_end_date[0], key="forecastenddate")
                st.selectbox("Reporting month:", date_range, index = index, format_func=lambda x: x.strftime('%b %Y'), key="reportingmonth")
                submit = st.form_submit_button(label='Submit', on_click = form_callback)

            st.write(forecast_details)