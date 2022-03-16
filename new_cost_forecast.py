import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid, JsCode
from myConfig import pageConfig, setSessionData
from cost_data import getCostSummaryData, getEACdata, processData, forecastCalcs,getCompanyJobOptions
from database_operations import readDetailsFromDatabase, writeCostDataToDatabase, writeDetailsToDatabase
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
import numpy as np
import pandas as pd

pageConfig()
setSessionData()

def userLogIn():
    """ User authenticates with Jonas Premier Credentials"""
    return

def getCompaniesAndJobs():
    """ Get a list of companies associated with the credentials"""
    allJobsData = getCompanyJobOptions()
    jobsData = allJobsData.drop_duplicates(subset=['Company_Code','Job_Number'])
    return jobsData[['Company_Code','Job_Number']]


jobsData = getCompaniesAndJobs()
st.session_state.count = st.session_state.count + 1
# st.write(st.session_state.count)
### Return: a list of companies User selects one.
# company_list = [""]
company_list = np.unique(np.array(jobsData.Company_Code)).tolist()
company_list.append("")
company_code = st.sidebar.selectbox("Company:", company_list, index = len(company_list)-1)


if company_code:
    job_list = jobsData['Job_Number'].where(jobsData['Company_Code']==company_code).tolist()
    job_list.append("")
    # st.session_state.job_number = st.sidebar.selectbox("Job:", job_list, index = len(job_list)-1 )
    st.session_state.job_number = st.sidebar.selectbox("Job:",['PD140479'])


if st.session_state.job_number != "":
    report_table_name = ('reportdetails_'+company_code+st.session_state.job_number).lower()
    cost_table_name = ('costdata_'+company_code+st.session_state.job_number).lower()

    ### Search database to see if 'Details' exist for that combo
    try:
        report_details = readDetailsFromDatabase(report_table_name)
        st.write(type(report_details.reporting_month[0]))
        # baseCostData = readDatabase(cost_table_name)
        baseCostData, job_start_date = processData(company_code,st.session_state.job_number,report_details.reporting_month[0],report_details.forecast_end_date[0])
        ## If NO --> report hasnt been generated previously so import data
    except:
        st.write(".....job not in database....")
            ### Set initial values for reporting date and end date
        reporting_month = pd.Period(datetime.today(),freq='M').end_time.date() - relativedelta(months=1)
        forecast_end_date = datetime.today() + relativedelta(months=3)
        baseCostData, job_start_date = processData(company_code,st.session_state.job_number,reporting_month,forecast_end_date)
        report_details = pd.DataFrame({
        'job_start_date': [job_start_date] ,
        'forecast_end_date': [forecast_end_date],
        'reporting_month': [reporting_month]
        })
        writeDetailsToDatabase(report_details, report_table_name)

    
    
    st.sidebar.write(f"Job start date: {report_details.job_start_date[0].strftime('%b %Y')}")

    my_range= pd.date_range(start=report_details.job_start_date[0], end=datetime.today(), freq='M').tolist()
    index = my_range.index(report_details.reporting_month[0])

    def form_callback():
        report_details.forecast_end_date[0] = st.session_state.forecastenddate
        report_details.reporting_month[0] = st.session_state.reportingmonth
        writeDetailsToDatabase(report_details, report_table_name)


    with st.sidebar.form(key='my_form'):
        st.date_input("Forecast end date:", report_details.forecast_end_date[0], key="forecastenddate")
        st.selectbox("Reporting month:", my_range, index = index, format_func=lambda x: x.strftime('%b %Y'), key="reportingmonth")
        submit = st.form_submit_button(label='Submit', on_click = form_callback)

    
    tableCostData = forecastCalcs(baseCostData, report_details)
    st.write(tableCostData)



    # st.sidebar.write("CHECK - reporting month:", report_details.reporting_month[0])


# st.sidebar.text_input("Company:", report.company_code)
# st.sidebar.text_input("Job:", report.job_number)
# st.sidebar.date_input("Job Start date:", report.start_date)
# st.sidebar.date_input("Forecast End date:", report.end_date)




# # baseCostData = processData(report)
# # writeToDatabase(baseCostData, cost_table_name)


# try:
#     baseCostData = readDatabase(cost_table_name)
# except:
#     st.write(f'Database table: {cost_table_name} does not exist --> import data. ')
#     baseCostData = processData(report)
#     writeCostDataToDatabase(baseCostData, cost_table_name)

# # st.write(report.end_date)
# # st.write(relativedelta(report.end_date, report.reporting_date).months)



# actual_children = configActualChildren(report.start_date, report.reporting_date)
# forecast_children = configForecastChildren(report.reporting_date, report.end_date)

# gridOptions, custom_css = configureGridOptions(actual_children, forecast_children)

# st.markdown("# Cost Forecast")

# grid_response = AgGrid(
#       dataframe = tableCostData,
#       # custom_css = custom_css,
#       gridOptions = gridOptions, 
#       height = 700,
#       enable_enterprise_modules=True,
#       fit_columns_on_grid_load=False,
#       key = 'unique_key',   #- set a key to stop the grid reinitialising when the dataframe changes
#       reload_data=True,  
#       data_return_mode='AS_INPUT',
#       update_mode='VALUE_CHANGED',   ## default
#     #   update_mode='MODEL_CHANGED',
#       allow_unsafe_jscode=True
#       )
# # st.write(actual_children)