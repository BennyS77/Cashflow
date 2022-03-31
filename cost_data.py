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
    eacData=eacData[['cost_group','Cost Item','Desc','Estimate At Completion']]
    # eacData['cost_group']='1'
    eacData = eacData.rename(columns={'Cost Item':'cost_item','Desc':'description','Estimate At Completion':'EAC'})
    return eacData


def createForecastDetails(cost_items, reporting_month, forecast_end_date):
    df = pd.DataFrame(cost_items)
    st.write
    # reporting_month = pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1)
    df['reporting_month']=reporting_month.date()
    # forecast_end_date = (datetime.today() + relativedelta(months=6)).date()
    df['forecast_end_date']=forecast_end_date
    df['item_start_date']=df['reporting_month'].apply(lambda x: pd.Period(x,freq='M').start_time.date() + relativedelta(months=1))
    df['item_end_date']=df['forecast_end_date']
    df['forecast_method']="Timeline"
    for i in range(1, len(pd.period_range(df['reporting_month'].iloc[0], df['forecast_end_date'].iloc[0], freq='M')),1):
        month=pd.Period(df['reporting_month'].iloc[0],freq='M').start_time.date() + relativedelta(months=i)
        df[month.strftime('%b_%y')+'_F%']=0
    return df


def filterFormatData(company, job, cost_data):
    cost_data = cost_data[cost_data['Company_Code']==company]
    cost_data = cost_data[cost_data['Job_Number']==job]
    cost_data = cost_data[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    cost_data['Fiscal_Period'] = pd.to_datetime(cost_data['Fiscal_Period'], format='%Y-%m')
    cost_data['Actual_Dollars']=cost_data['Actual_Dollars'].astype(float)
    cost_data['Calendar_Period'] = cost_data['Fiscal_Period'].apply(lambda x: x - relativedelta(months=6)+relativedelta(days=15))
    cost_data.drop(['Fiscal_Period'], axis=1, inplace=True)
    first_month = cost_data['Calendar_Period'].min()
    date_range = pd.date_range(start=first_month, end=pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1), freq='M').tolist()
    return cost_data, date_range


def calc_cost_per_month_and_ACTD(cost_by_fiscal_period, first_month, last_month):
    # lastMonth = reporting_date
    d_end=[0]*len(pd.period_range(first_month, last_month, freq='M'))
    for i in range(len(pd.period_range(first_month, last_month, freq='M'))):
            d_start=pd.Period(first_month,freq='M').start_time.date() + relativedelta(months=i)
            d_end[i]=pd.Period(first_month,freq='M').end_time.date() + relativedelta(months=i)
            cost_by_fiscal_period[d_end[i].strftime('%b_%y')+'_$'] = cost_by_fiscal_period.apply(lambda x: x.Actual_Dollars if x.Calendar_Period>=d_start and x.Calendar_Period<=d_end[i] else 0, axis=1)
    cost_by_fiscal_period.drop(['Actual_Dollars','Calendar_Period'], axis=1, inplace=True)
    cost_by_fiscal_period=cost_by_fiscal_period.groupby(['Cost_Item']).apply(lambda x: x.sum())
    cost_by_fiscal_period.drop(['Cost_Item'], axis=1, inplace=True)
    cost_by_fiscal_period['ACTD'] = cost_by_fiscal_period.sum(axis=1)
    cost_by_fiscal_period.reset_index(inplace=True)
    cost_by_fiscal_period = cost_by_fiscal_period.rename(columns = {'Cost_Item':'cost_item'})
    return cost_by_fiscal_period


def merge_eac_and_calc_percent(cost_data, eac_data, first_month, last_month):
    cost_data = pd.merge(cost_data, eac_data, on='cost_item', how='left')
    cost_data.fillna({'Description':'unknown','EAC':0,'cost_group':'1'}, inplace=True)
    this_range = pd.period_range(first_month, last_month, freq='M')
    for i, item in enumerate(this_range):
        if i == 0:
            cost_data[item.strftime('%b_%y')+'_%']=cost_data.apply(lambda x: x[item.strftime('%b_%y')+'_$']/x.EAC if x.EAC>0 else 0, axis=1)
        else:
            cost_data[this_range[i].strftime('%b_%y')+'_%'] = (
                            cost_data.apply(lambda x: x[this_range[i].strftime('%b_%y')+'_$']/x.EAC + x[this_range[i-1].strftime('%b_%y')+'_%'] if x.EAC>0 else 0, axis=1) 
                            )
    return cost_data


def myFunc(x):
    businessDaysInMonth = np.busday_count(x['current_month'], x['current_month'] + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
    if x['daysLeft']>businessDaysInMonth:
        workDaysInMonth =  businessDaysInMonth 
    else:
        workDaysInMonth = x['daysLeft']
    return workDaysInMonth


def forecast_calcs(cost_data, forecast_data):
    cost_data['ETC'] = cost_data['EAC'] - cost_data['ACTD']
    # cost_table_data = pd.merge(cost_data, forecast_data, on='cost_item', how='left')
    cost_table_data = pd.merge(cost_data, forecast_data, on='cost_item', how='inner')
    # cost_table_data.fillna(method='pad', inplace=True)
    cost_table_data['numDaysDuration'] = cost_table_data.apply(lambda x: np.busday_count(x.item_start_date.date(), x.item_end_date.date(), weekmask=[1,1,1,1,1,0,0]), axis = 1)
    cost_table_data['accumPercent'] = cost_table_data.apply(lambda x: x['ACTD']/x['EAC']*100 if x['EAC']>0 else 0, axis=1)
    cost_table_data['percentPerDay'] = cost_table_data.apply(lambda x: x['ETC']/x['EAC']*100/ x['numDaysDuration'] if x['EAC']>0 else 0, axis=1)
    cost_table_data['daysLeft'] = cost_table_data['numDaysDuration']
    for i in range(1, len(pd.period_range(cost_table_data['reporting_month'].iloc[0], cost_table_data['forecast_end_date'].iloc[0], freq='M')),1):
        month=pd.Period(cost_table_data['reporting_month'].iloc[0],freq='M').start_time.date() + relativedelta(months=i)
        cost_table_data['current_month']=month
        cost_table_data[month.strftime('%b %y')+'workDaysInMonth']=cost_table_data.apply(myFunc, axis=1)
        cost_table_data['workDaysInMonth']=cost_table_data.apply(myFunc, axis=1)
        cost_table_data['accumPercent'] = cost_table_data['accumPercent'] + cost_table_data['workDaysInMonth']*cost_table_data['percentPerDay']

        cost_table_data[month.strftime('%b_%y')+'_F%'] = cost_table_data.apply(
                                        lambda x: x['accumPercent'] if x['forecast_method'] == 'Timeline' else x[month.strftime('%b_%y')+'_F%'], axis = 1
        )
        cost_table_data[month.strftime('%b_%y')+'_F$'] = cost_table_data['workDaysInMonth']*cost_table_data['percentPerDay']/100 *cost_table_data['EAC']
        cost_table_data['daysLeft'] = cost_table_data['daysLeft'] - cost_table_data['workDaysInMonth']
    return cost_table_data

def calculate_pinned_row_data(cost_display_data, date_range, reporting_month, forecast_end_date):
    rowDataDict={"autoGroup":"Total Costs:","EAC":cost_display_data['EAC'].sum(),"ACTD":cost_display_data['ACTD'].sum(),"ETC":cost_display_data['ETC'].sum()}
    my_range = pd.date_range(start=date_range[0], end=reporting_month, freq='M').tolist()
    for i, item in enumerate(my_range):
        rowDataDict.update({item.strftime('%b_%y')+'_$':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum())})
        rowDataDict.update({item.strftime('%b_%y')+'_%':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum()/cost_display_data['EAC'].sum())})
    forecast_date_range = pd.date_range(start = reporting_month+relativedelta(months=1), end = forecast_end_date+relativedelta(months=1), freq='M').tolist()
    for i, item in enumerate(forecast_date_range):
        rowDataDict.update({item.strftime('%b_%y')+'_F$':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum())})
        rowDataDict.update({item.strftime('%b_%y')+'_F%':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum()/cost_display_data['EAC'].sum())})
    return [rowDataDict]