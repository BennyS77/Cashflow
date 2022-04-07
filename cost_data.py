from pyrsistent import v
import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import requests
import numpy as np
from database_operations import writeDetailsToDatabase, readDetailsFromDatabase, drop_table

@st.experimental_memo()
def get_company_and_job_names():
    """  
        Get Jobs data via OData and save to Session State variables 
    """
    dataset = 'JobContactsViews'
    URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/'+dataset+'/?$format=json'
    username=st.session_state.creds['username']
    password=st.session_state.creds['password']
    response = requests.get(URL, auth = (username,password))
    dict_1=response.json() 
    list_1 = dict_1['value']
    df_1 = pd.DataFrame(list_1)
    company_and_job_names = df_1[['Company_Code','Job_Number']]
    company_list = company_and_job_names['Company_Code'].drop_duplicates().tolist()
    company_list.append("")
    return company_and_job_names, company_list


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


def get_eac_data():
    eac_data= pd.read_csv('CostAtCompletion.csv')
    eac_data=eac_data[['cost_group','Cost Item','Desc','Estimate At Completion']]
    eac_data = eac_data.rename(columns={'Cost Item':'cost_item','Desc':'description','Estimate At Completion':'EAC'})
    return eac_data


def createForecastDetails(cost_items, reporting_month, forecast_end_date):
    df = pd.DataFrame(cost_items)
    df['reporting_month']=reporting_month.date()
    df['forecast_end_date']=forecast_end_date
    df['item_start_date']=df['reporting_month'].apply(lambda x: pd.Period(x,freq='M').start_time.date() + relativedelta(months=1))
    df['item_end_date']=df['forecast_end_date']
    df['forecast_method']="Timeline"
    for i in range(1, len(pd.period_range(df['reporting_month'].iloc[0], df['forecast_end_date'].iloc[0], freq='M')),1):
        month=pd.Period(df['reporting_month'].iloc[0] + relativedelta(months=i) , freq='M').start_time.date() 
        # month=pd.Period(df['reporting_month'].iloc[0],freq='M').start_time.date() + relativedelta(months=i)
        df[month.strftime('%b_%y')+'_F%']=0
    return df


def get_cost_data_and_date_range():
    cost_data = getJobCostByFiscalPeriod(st.session_state.creds)
    cost_data = cost_data[cost_data['Company_Code']==st.session_state.company]
    cost_data = cost_data[cost_data['Job_Number']==st.session_state.job]
    cost_data = cost_data[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    cost_data['Fiscal_Period'] = pd.to_datetime(cost_data['Fiscal_Period'], format='%Y-%m')
    cost_data['Actual_Dollars']=cost_data['Actual_Dollars'].astype(float)
    cost_data['Calendar_Period'] = cost_data['Fiscal_Period'].apply(lambda x: x-relativedelta(months=6)+relativedelta(days=15))
    cost_data.drop(['Fiscal_Period'], axis=1, inplace=True)
    cost_data.drop(cost_data[cost_data['Calendar_Period']<datetime(2021,7,1)].index, inplace=True)
    # st.session_state.cost_data = cost_data
    first_month = cost_data['Calendar_Period'].min()
    end_month = pd.Period(datetime.today() + relativedelta(months=-1), freq='M').end_time.date()
    # st.session_state.date_range = pd.date_range(start=first_month, end=end_month, freq='M').tolist()
    date_range = pd.date_range(start=first_month, end=end_month, freq='M').tolist()
    # st.session_state.date_range.append("")
    date_range.append("")
    return cost_data, date_range


def calc_cost_per_month_and_ACTD(cost_by_fiscal_period, first_month, last_month):
    # lastMonth = reporting_date
    d_end=[0]*len(pd.period_range(first_month, last_month, freq='M'))
    for i in range(len(pd.period_range(first_month, last_month, freq='M'))):
            d_start=pd.Period(first_month+relativedelta(months=i), freq='M').start_time.date()
            d_end[i]=pd.Period(first_month+relativedelta(months=i), freq='M').end_time.date() 
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
    if x['item_start_date'] <= x['current_month']:
        businessDaysInMonth = np.busday_count(x['current_month'], x['current_month'] + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
    if x['item_start_date'] > x['current_month'] and x['item_start_date'] < x['current_month'] + relativedelta(months=1):
        businessDaysInMonth = np.busday_count(x['item_start_date'].date(), x['current_month'] + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
    if x['item_start_date'] >= x['current_month'] + relativedelta(months=1):
        businessDaysInMonth = 0

    if x['daysLeft']>businessDaysInMonth:
        workDaysInMonth =  businessDaysInMonth 
    else:
        workDaysInMonth = x['daysLeft']
    return workDaysInMonth


def forecast_calcs(cost_data, forecast_data):
    cost_data['ETC'] = cost_data['EAC'] - cost_data['ACTD']
    # cost_table_data = pd.merge(cost_data, forecast_data, on='cost_item', how='left')
    
    cost_table_data = pd.merge(cost_data, forecast_data, on='cost_item', how='inner')
    # st.write('cost_table_data')
    # st.write(cost_table_data.iloc[:5,42:])
    # cost_table_data.fillna(method='pad', inplace=True)
    cost_table_data['numDaysDuration'] = cost_table_data.apply(lambda x: np.busday_count(x.item_start_date.date(), x.item_end_date.date(), weekmask=[1,1,1,1,1,0,0]), axis = 1)
    cost_table_data['accumPercent'] = cost_table_data.apply(lambda x: x['ACTD']/x['EAC']*100 if x['EAC']>0 else 0, axis=1)
    cost_table_data['percentPerDay'] = cost_table_data.apply(lambda x: x['ETC']/x['EAC']*100/ x['numDaysDuration'] if x['EAC']>0 else 0, axis=1)
    cost_table_data['daysLeft'] = cost_table_data['numDaysDuration']
    range_of_future_months = pd.period_range(cost_table_data['reporting_month'].iloc[0], cost_table_data['forecast_end_date'].iloc[0], freq='M') 
    for i in range(1, len(range_of_future_months),1):
        month=pd.Period(cost_table_data['reporting_month'].iloc[0],freq='M').start_time.date() + relativedelta(months=i)
        cost_table_data['current_month']=month
        cost_table_data[month.strftime('%b %y')+'workDaysInMonth']=cost_table_data.apply(myFunc, axis=1)
        cost_table_data['workDaysInMonth']=cost_table_data.apply(myFunc, axis=1)
        cost_table_data['accumPercent'] = cost_table_data['accumPercent'] + cost_table_data['workDaysInMonth']*cost_table_data['percentPerDay']

        cost_table_data[month.strftime('%b_%y')+'_F%'] = cost_table_data.apply(
                                        lambda x: x['accumPercent'] if x['forecast_method'] == 'Timeline' else x[month.strftime('%b_%y')+'_F%'], axis = 1 )

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


def get_forecast_data_for_reporting_month():
    """ 
    If table for job exists in the database, read that into a dataframe.
    If table for job does NOT exist in the database, create a table with default values.
    Extract data relating to selected reporting month.
    """
    try:
        forecast_details = readDetailsFromDatabase(('forecast_details_'+st.session_state.company+st.session_state.job).lower())
        st.session_state.reporting_month_data_exists = True
    except:
        eac_data = getEACdata()
        forecast_details = createForecastDetails(eac_data.cost_item, st.session_state.reporting_month, st.session_state.forecast_end_date)
        writeDetailsToDatabase(forecast_details, ('forecast_details_'+st.session_state.company+st.session_state.job).lower())
    return forecast_details, forecast_details.loc[forecast_details['reporting_month'] == st.session_state.reporting_month]


def calculate_cost_data_for_the_grid(cost_by_fiscal_period, forecast_data_for_reporting_month, date_range):
    eac_data = get_eac_data()
    cost_with_ACTD = calc_cost_per_month_and_ACTD(cost_by_fiscal_period, date_range[0], st.session_state.reporting_month)
    ### The order/details of the merge needs to be updated 
    cost_data = merge_eac_and_calc_percent(cost_with_ACTD, eac_data, date_range[0], st.session_state.reporting_month)
    grid_cost_data = forecast_calcs(cost_data, forecast_data_for_reporting_month)
    pinned_row_data = calculate_pinned_row_data(grid_cost_data, date_range, st.session_state.reporting_month, st.session_state.forecast_end_date)
    return grid_cost_data, pinned_row_data

# def get_cost_data_for_the_grid():
#     eac_data = get_eac_data()


def update_reporting_month():
    """ Change grid key so that the grid re-initialises after changing the date"""
    st.session_state.grid_key = st.session_state.grid_key + 1
    st.session_state.ready_for_grid = True

def create_forecast_data_table():
    st.write("  Create new Forecast Data table and write to the database  ")
    eac_data = get_eac_data()
    forecast_data = createForecastDetails(eac_data.cost_item, st.session_state.reporting_month, st.session_state.forecast_end_date)
    writeDetailsToDatabase(forecast_data)
    return



def create_reporting_month_data(the_details):
    """
    append Forecast Data table with data for Reporting Month
    """
    eac_data = getEACdata()
    new_forecast_details = createForecastDetails(eac_data.cost_item, st.session_state.reporting_month, st.session_state.forecast_end_date)
    writeDetailsToDatabase(new_forecast_details, 'temp')
    new_forecast_details = readDetailsFromDatabase('temp')
    forecast_details = the_details.append(new_forecast_details)
    writeDetailsToDatabase(forecast_details, ('forecast_details_'+st.session_state.company+st.session_state.job).lower())
    st.session_state.grid_key = st.session_state.grid_key + 1
    st.session_state.ready_for_grid = True
    return forecast_details



def after_selecting_company():
    """
        Create a Job list based on the selected Company
    """
    st.session_state.job_list = st.session_state.companies_and_jobs['Job_Number'].where(st.session_state.companies_and_jobs['Company_Code']==st.session_state.company).tolist()
    st.session_state.job_list.append("")

def after_selecting_job():
    st.session_state.cost_data,st.session_state.date_range = get_cost_data_and_date_range()
    
def after_selecting_reporting_month():
    """ If table exists, and if reporting_month data exists, get required forecast data and forecast_end_date  """
    # drop_table()
    try:
        st.session_state.all_forecast_data = readDetailsFromDatabase()
        """  Table exists in the database.  """
        st.session_state.reporting_month_forecast_data = st.session_state.all_forecast_data.loc[st.session_state.all_forecast_data['reporting_month'] == st.session_state.reporting_month]
        max_forecast_end_date =  st.session_state.all_forecast_data['forecast_end_date'].max()
        most_recent_reporting_month = st.session_state.all_forecast_data['reporting_month'].max()
        # st.write('most_recent_reporting_month:')
        # st.write(most_recent_reporting_month)
        st.session_state.forecast_table_exists = True
        if len(st.session_state.reporting_month_forecast_data)>0:
            """  Table exists in the database, and data IS available for selected Reporting Month.  """
            st.session_state.reporting_month_data_exists = True
            st.session_state.ready_for_grid = True
        else:
            """ Reporting Month data does NOT exist - create:"""
            most_recent_data = st.session_state.all_forecast_data.loc[st.session_state.all_forecast_data['reporting_month'] == most_recent_reporting_month]
            # st.write('most_recent_data:')
            # st.write(most_recent_data)
            new_month_data = most_recent_data
            new_month_data['reporting_month'] = st.session_state.reporting_month
            new_month_data['forecast_end_date'] = max_forecast_end_date
            # st.write('new_month_data:')
            # st.write(new_month_data)
            new_all_data = st.session_state.all_forecast_data.append(new_month_data)
            # st.write('new_all_data:')
            # st.write(new_all_data)
            writeDetailsToDatabase(new_all_data)
            st.session_state.reporting_month_forecast_data = new_all_data
            st.session_state.ready_for_grid = True
            
            # st.session_state.reporting_month_data_exists = False
        st.session_state.forecast_end_date =  st.session_state.reporting_month_forecast_data['forecast_end_date'].iloc[0]
    except:
        """  Data for the Job does NOT exist in the database. """
        st.session_state.forecast_table_exists = False


def login_form(credentials):
    """
        When credentials are submitted - retrieve Company and Job details.
    """
    st.session_state.login_confirmed = True
    st.session_state.creds = credentials
    st.session_state.companies_and_jobs, st.session_state.company_list = get_company_and_job_names()


def user_input_variables():
    """
        Define user input variables and what happens when they are changed
    """

    st.sidebar.selectbox( label = "Company:",
                options = st.session_state.company_list,
                index = len(st.session_state.company_list)-1,
                on_change = after_selecting_company,
                key ='company',
                disabled = not st.session_state.login_confirmed
                )
    st.session_state.job_list = ["PD140479", "TMR456", '']
    st.sidebar.selectbox( label = "Job:",
                options = st.session_state.job_list,
                index = len(st.session_state.job_list)-1,
                on_change = after_selecting_job,
                key = 'job',
                disabled = not st.session_state.login_confirmed
                )
    st.sidebar.selectbox( label = "Reporting Month:",
                options = st.session_state.date_range,
                index = (len(st.session_state.date_range)-1),
                format_func=lambda x: x.strftime('%b %Y') if x!="" else x,
                on_change = after_selecting_reporting_month,
                key= 'reporting_month',
                disabled= not st.session_state.login_confirmed)

    if st.session_state.forecast_table_exists == False:
        """ Only show if   """
        st.sidebar.markdown("# ")
        st.sidebar.date_input(
            label = "Change Forecast End Date:", 
            on_change = create_forecast_data_table,
            key= 'forecast_end_date',
            disabled= not st.session_state.login_confirmed
            )
    
    if st.session_state.login_confirmed == False:
        st.sidebar.markdown("# ")
        st.sidebar.markdown("## Login")
        with st.sidebar.form('credentials', clear_on_submit=True):
            # st.markdown("## Login")
            client_id = st.text_input('Client ID:', 'test client') 
            username = st.text_input('Username:','test username')  
            password = st.text_input('Password:',type="password") 
            client_id = '317016'
            username = 'BenStewart'
            password = 'Woerifjoi439856'
            creds_dict = {"username":client_id+'\\'+username, "password":password}
            st.form_submit_button('Submit', kwargs = dict(credentials = creds_dict), on_click = login_form)
    # else:
    #     st.sidebar.write("Log out.")
    
    return
