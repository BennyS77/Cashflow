import streamlit as st
from datetime import datetime
from my_config import pageConfig, setSessionData, setLogIn
from cost_data import getCompanyAndJobList, getJobCostByFiscalPeriod, getEACdata, getJobList, createForecastDetails

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
            forecast_details = createForecastDetails(eac_data.costitem)

            ## 8
            ###... Write to database ...###


            ## 9
            

            st.write(forecast_details)


            st.sidebar.write(selected_company)
            st.sidebar.write(selected_job)