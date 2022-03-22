from pyrsistent import v
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import numpy as np


@st.experimental_memo()
def getCompanyAndJobList(creds):
    import requests
    dataset = 'JobContactsViews'
    URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/'+dataset+'/?$format=json'
    username=creds['username']
    password=creds['password']
    response = requests.get(URL, auth = (username,password))
    dict_1=response.json() 
    list_1 = dict_1['value']
    df_1 = pd.DataFrame(list_1)
    df_1 = df_1[['Company_Code','Job_Number']]
    company_list = df_1['Company_Code'].drop_duplicates().tolist()
    company_list.append("")
    return company_list, df_1

def getJobList(company, companies_and_jobs):
    job_list = companies_and_jobs['Job_Number'].where(companies_and_jobs['Company_Code']==company).tolist()
    job_list.append("")
    return job_list


@st.experimental_memo()
def getJobCostByFiscalPeriod(creds):
    dataset = 'JobCostSummaryByFiscalPeriods' 
    URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/'+dataset+'/?$format=json'
    # URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/?$format=json'
    username=creds['username']
    password=creds['password']
    response = requests.get(URL, auth = (username,password))
    # st.write(response.status_code)
    dict_1 = response.json()  ## create a dictionary 2 keys - 'odata.metadata' and 'value'.  Value is a list of dictionaries
    list_1 = dict_1['value']
    df_1 = pd.DataFrame(list_1)
    return df_1[['Fiscal_Period','Job_Number','Cost_Item','Actual_Dollars','Company_Code']]


def getEACdata():
    eacData= pd.read_csv('CostAtCompletion.csv')
    eacData=eacData[['Cost Item','Desc','Estimate At Completion']]
    eacData['costgroup']='1'
    eacData = eacData.rename(columns={'Cost Item':'costitem','Desc':'description','Estimate At Completion':'eac'})
    return eacData


def createForecastDetails(costitems):
    df = pd.DataFrame(costitems)
    df['reporting_month']=pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1)
    df['forecast_end_date']=(datetime.today() + relativedelta(months=6)).date()
    df['item_start_date']=df['reporting_month'].apply(lambda x: pd.Period(x,freq='M').start_time.date() + relativedelta(months=1))
    df['item_end_date']=df['forecast_end_date']
    df['forecast_method']="Timeline"
    for i in range(1, len(pd.period_range(df['reporting_month'].iloc[0], df['forecast_end_date'].iloc[0], freq='M')),1):
        month=pd.Period(df['reporting_month'].iloc[0],freq='M').start_time.date() + relativedelta(months=i)
        df[month.strftime('%b %y')]=0
    return df


def processData(company_code, job_number, reporting_date, end_date):
    # allActualCostData = getCostSummaryData()
    # eacData = getEACdata()
    companyActualCostData = allActualCostData[allActualCostData['Company_Code']==company_code]
    jobActualCostData = companyActualCostData[companyActualCostData['Job_Number']==job_number]
    costData = jobActualCostData[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    costData['Fiscal_Period'] = pd.to_datetime(costData['Fiscal_Period'], format='%Y-%m')
    costData['Actual_Dollars']=costData['Actual_Dollars'].astype(float)
    costData['Calendar_Period'] = costData['Fiscal_Period'].apply(lambda x: x - relativedelta(months=6)+relativedelta(days=15))
    costData.drop(['Fiscal_Period'], axis=1, inplace=True)
    firstMonth = costData['Calendar_Period'].min()
    # st.session_state.report_details.start_date = firstMonth
    # lastMonth = costData['Calendar_Period'].max()
    lastMonth = reporting_date
    d_end=[0]*len(pd.period_range(firstMonth, lastMonth, freq='M'))
    for i in range(len(pd.period_range(firstMonth, lastMonth, freq='M'))):
            d_start=pd.Period(firstMonth,freq='M').start_time.date() + relativedelta(months=i)
            d_end[i]=pd.Period(firstMonth,freq='M').end_time.date() + relativedelta(months=i)
            costData[d_end[i].strftime('%b %y')] = costData.apply(lambda x: x.Actual_Dollars if x.Calendar_Period>=d_start and x.Calendar_Period<=d_end[i] else 0, axis=1)
    costData.drop(['Actual_Dollars','Calendar_Period'], axis=1, inplace=True)
    costData=costData.groupby(['Cost_Item']).apply(lambda x: x.sum())
    costData.drop(['Cost_Item'], axis=1, inplace=True)
    st.write("CostData:")
    st.write(costData)
    col_list = costData.columns.values.tolist() 
    for i in range(len(col_list)):
        col_list[i]=datetime.strptime(col_list[i], "%b %y")
    st.write(col_list)
    st.write(min(col_list))
    st.write(type(col_list[0]))
    costData['ACTD'] = costData.sum(axis=1)
    costData.reset_index(inplace=True)
    costData = costData.rename(columns = {'Cost_Item':'costitem'})
    costData = pd.merge(costData, eacData, on='costitem', how='left')
    costData.fillna({'Description':'unknown','EAC':0,'costGroup':'1'}, inplace=True)
    for i in range(len(pd.period_range(firstMonth, lastMonth, freq='M'))):
        ### change this to cumulative percentage??
        costData[d_end[i].strftime('%b %y')+' A%']=costData.apply(lambda x: x[d_end[i].strftime('%b %y')]/x.EAC if x.EAC>0 else 0, axis=1)
    costData['startDate']=pd.Period(reporting_date,freq='M').start_time.date() + relativedelta(months=1)
    costData['endDate']= end_date.date()  ## convert it to datetime
    costData['forecastmethod']='Timeline'
    
    return costData, firstMonth


def myFunc(x):
    businessDaysInMonth = np.busday_count(x['startDate'], x['startDate'] + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
    if x['daysLeft']>businessDaysInMonth:
        workDaysInMonth =  businessDaysInMonth 
    else:
        workDaysInMonth = x['daysLeft']
    return workDaysInMonth


def forecastCalcs(grid_data, r1):
    grid_data['ETC'] = grid_data['EAC'] - grid_data['ACTD']
    # grid_data['startDate'] = grid_data.apply(lambda x: x.startDate.date(), axis=1)
    # grid_data['endDate'] = grid_data.apply(lambda x: x.endDate.date(), axis=1)
    # st.write(type(grid_data['startDate'].iloc[0]))
    # st.write(type(grid_data['endDate'].iloc[0]))
    grid_data['numDaysDuration'] = grid_data.apply(lambda x: np.busday_count(x.startDate, x.endDate, weekmask=[1,1,1,1,1,0,0]), axis = 1)
    grid_data['accumPercent'] = grid_data.apply(lambda x: x['ACTD']/x['EAC']*100 if x['EAC']>0 else 0, axis=1)
    grid_data['percentPerDay'] = grid_data.apply(lambda x: x['ETC']/x['EAC']*100/ x['numDaysDuration'] if x['EAC']>0 else 0, axis=1)
    grid_data['daysLeft'] = grid_data['numDaysDuration']
    for i in range(1, (relativedelta(r1.forecast_end_date[0], r1.reporting_month[0]).months)+3, 1):
        thisMonth = pd.Period(r1.reporting_month[0],freq='M').start_time.date() + relativedelta(months=i)
        grid_data['workDaysInMonth']=grid_data.apply(myFunc, axis=1)
        grid_data['accumPercent'] = grid_data['accumPercent'] + grid_data['workDaysInMonth']*grid_data['percentPerDay']
        grid_data[thisMonth.strftime('%b %y')+' F%'] = grid_data['accumPercent']
        grid_data[thisMonth.strftime('%b %y')+' F$'] = grid_data['workDaysInMonth']*grid_data['percentPerDay']*grid_data['EAC']
        grid_data['daysLeft'] = grid_data['daysLeft'] - grid_data['workDaysInMonth']
    return grid_data
