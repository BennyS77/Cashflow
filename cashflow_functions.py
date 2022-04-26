import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid
from aggrid_functions_cost import config_actual_cost_children, config_forecast_cost_children, configure_cost_grid_options
from database_operations import table_names, read_table_from_database

def page_layout():
    """
        Set the page template
    """
    def cost_click():
        st.session_state.cost_clicked = True
        st.session_state.revenue_clicked = False
        st.session_state.summary_clicked = False
    def revenue_click():
        st.session_state.revenue_clicked = True
        st.session_state.cost_clicked = False
        st.session_state.summary_clicked = False
    def summary_click():
        st.session_state.summary_clicked = True
        st.session_state.cost_clicked = False
        st.session_state.revenue_clicked = False

    html_heading = '<h1 style="text-align: left;padding:0px;padding-bottom:0px;margin:0px">Cashflow</h1>'
    html_line = """<hr style="height:4px;padding:0px;margin:0px;border:none;background-color:rgb(242,244,246);" /> """
    html_sidebar_line = """<hr style="height:4px;padding:0px;margin:0px;border:none;background-color:rgb(250,250,250);" /> """
    html_underline = """<hr style="height:4px;padding:0px;margin:0px;width:25%;background-color:rgb(150,5,5);" /> """
    
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    with col1:
        st.markdown(html_heading, unsafe_allow_html=True)  
    with col2:  
        st.button(" COST ",  on_click=cost_click)
        if st.session_state.cost_clicked == True:
            st.markdown(html_underline, unsafe_allow_html=True)
    with col3:
        st.button("REVENUE", on_click=revenue_click)
        if st.session_state.revenue_clicked == True:
            st.markdown(html_underline, unsafe_allow_html=True)
    with col4:
        st.button("SUMMARY", on_click=summary_click)
        if st.session_state.summary_clicked == True:
            st.markdown(html_underline, unsafe_allow_html=True)
    st.markdown(html_line, unsafe_allow_html=True)
    st.sidebar.markdown("# Report settings:")
    st.sidebar.markdown(html_sidebar_line, unsafe_allow_html=True)
    return

def user_login():
    """  User login """
    def confirm_login():
        st.session_state.login_confirmed = True
        st.session_state.credentials = {"username":st.session_state.client_id+'\\'+st.session_state.username, "password":st.session_state.password}
        return
    with st.sidebar.form(key='my_form', clear_on_submit=True):
        st.text_input(label="client_id", key='client_id', value = '321081')
        st.text_input(label="username", key='username', value = 'JP.API')
        st.text_input('Password:', key='password', type="password", value = 'JQ24Ty3H4sr6A1PWa')
        st.form_submit_button("submit", on_click = confirm_login)
    return


@st.experimental_memo()
def fetch_Odata(dataset, columns='*', filter=""):
    URL = "https://reporting.jonas-premier.com/OData/ODataService.svc/"+dataset
    query = "?$filter="+filter + "&$select="+columns + "&$format=json"
    user_auth = (st.session_state.credentials['username'], st.session_state.credentials['password']) 
    # user_auth = ('321059\KeypaySyncAPI', 'gXs6SwBkDTKmw8Hv')     # Colibrico
    # user_auth = ('321081\JP.API',        'JQ24Ty3H4sr6A1PWa')    # Reitsma
    # user_auth = ('321078/KeypaySyncAPI', 'MACcB8xtNNJ65fk6')	# Phase3
    # user_auth = ('316006/KeypaySyncAPI', 'YRSCpA65hHRFRUmS')	# Akura/Wallandra
    # user_auth = ('321059/KeypaySyncAPI', 'gXs6SwBkDTKmw8Hv')	# Colbrico Breakaway
    # user_auth = ('811010/KeypaySyncAPI', 'cdVfcHHeHL5v2EzJ')	# Jonas Premier Test
    # user_auth = ('319029/KeypaySyncAPI', 'U4kT4tePBs2JqvKD')	# Ecowise
    # user_auth = ('319006/JP.API',	     'tYzxU2fQuJvrVSgJ')	# Neverstop

    response = requests.get(URL+query, auth = user_auth)
    # st.write(response.status_code)
    dict_1 = response.json()  ## create a dictionary 2 keys - 'odata.metadata' and 'value'.  Value is a list of dictionaries
    list_1 = dict_1['value']
    return pd.DataFrame(list_1)


def get_odata():
    URL = """  https://reporting.jonas-premier.com/OData/ODataService.svc/APPostedInvoices?$filter=Company eq 'ES' and Transaction_Date 
        gt datetime'2021-04-21' and Transaction_Date lt datetime'2022-04-22';Namespaces to Include=*;Max Received Message Size=4398046511104;
        Integrated Security=Basic;User ID=319029\OdataAgent;Persist Security Info=false;Base Url="https://reporting.jonas-premier.com/OData/ODataService.svc/APPostedInvoices?$filter=Company 
        eq 'ES' and Transaction_Date gt datetime'2021-04-21' and Transaction_Date lt datetime'2022-04-22'" """
    user_auth = ('321059\KeypaySyncAPI', 'gXs6SwBkDTKmw8Hv')     # Colibrico
    response = requests.get(URL, auth = user_auth)
    st.write(response.status_code)
    dict_1 = response.json()  ## create a dictionary 2 keys - 'odata.metadata' and 'value'.  Value is a list of dictionaries
    list_1 = dict_1['value']
    return pd.DataFrame(list_1)


def get_odata_list():
    URL = "https://reporting.jonas-premier.com/OData/ODataService.svc?$format=json"
    user_auth = ('321059\KeypaySyncAPI', 'gXs6SwBkDTKmw8Hv')     # Colibrico
    response = requests.get(URL, auth = user_auth)
    st.write(response.status_code)
    dict_1 = response.json()  ## create a dictionary 2 keys - 'odata.metadata' and 'value'.  Value is a list of dictionaries
    list_1 = dict_1['value']
    return pd.DataFrame(list_1)




def set_all_cost_data():
    cost_data = get_JobCostByFiscalPeriod()
    # cost_data = cost_data[cost_data['Company_Code']==st.session_state.company]
    cost_data = cost_data[cost_data['Job_Number']==st.session_state.job]
    cost_data = cost_data[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    cost_data['Fiscal_Period'] = pd.to_datetime(cost_data['Fiscal_Period'], format='%Y-%m')
    cost_data['Actual_Dollars']=cost_data['Actual_Dollars'].astype(float)
    cost_data['Calendar_Period'] = cost_data['Fiscal_Period'].apply(lambda x: x-relativedelta(months=6)+relativedelta(days=15))
    cost_data.drop(['Fiscal_Period'], axis=1, inplace=True)
    cost_data.drop(cost_data[cost_data['Calendar_Period']<datetime(2021,7,1)].index, inplace=True)
    first_month = cost_data['Calendar_Period'].min()
    end_month = pd.Period(datetime.today() + relativedelta(months=-1), freq='M').end_time.date()
    date_range = pd.date_range(start=first_month, end=end_month, freq='M').tolist()
    date_range.append("")
    st.session_state.all_cost_data = cost_data
    st.session_state.date_range = date_range
    st.session_state.cost_data_retrieved = True
    return
    

def select_company_and_job(testing):
    if not st.session_state.job and not st.session_state.company or testing:
        r_status, st.session_state.cost_by_fiscal_period = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
        st.session_state.company_list = st.session_state.cost_by_fiscal_period['Company_Code'].drop_duplicates().tolist()
        st.session_state.company_list.append("")
        st.session_state.job_list = st.session_state.cost_by_fiscal_period['Job_Number'].drop_duplicates().tolist()
        st.session_state.job_list.append("")

    st.sidebar.selectbox(label = "Company:",
                        options = st.session_state.company_list,
                        key ='company' 
                        )
    st.sidebar.selectbox(label = "Job:",
                        options = st.session_state.job_list,
                        key = 'job')
    return



def get_cost_estimate_data(job):
    df_1 = fetch_Odata(
                dataset = 'JobReportByCostItemAndCostTypes', 
                columns = "Division,Cost_Item,Cost_Item_Description,Estimate_At_Completion",
                filter = "Job_Number eq '"+job+"'"
                )
    df_1 = df_1.rename(columns = {'Cost_Item':'cost_item','Estimate_At_Completion':'EAC'})
    df_1['EAC']=df_1['EAC'].astype(float)
    df_1 = df_1.groupby(['cost_item']).agg({'EAC':['sum'],'Division':['first'],'Cost_Item_Description':['first']})
    df_1 = df_1.droplevel(level=1, axis=1)
    df_1.reset_index(level=0, inplace=True)
    df_1['EAC']=df_1['EAC'].astype(float)
    return df_1


def get_all_cost_data():
    # st.sidebar.write("Formatting cost data")
    cost_data = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
    cost_data = cost_data[cost_data['Company_Code']==st.session_state.company]
    cost_data = cost_data[cost_data['Job_Number']==st.session_state.job]
    cost_data = cost_data[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    cost_data['Fiscal_Period'] = pd.to_datetime(cost_data['Fiscal_Period'], format='%Y-%m')
    cost_data['Actual_Dollars']=cost_data['Actual_Dollars'].astype(float)
    cost_data['Calendar_Period'] = cost_data['Fiscal_Period'].apply(lambda x: x-relativedelta(months=6)+relativedelta(days=15))
    cost_data.drop(['Fiscal_Period'], axis=1, inplace=True)
    # st.write("cleaned-up cost data")
    # st.write(cost_data)
    # cost_data.drop(cost_data[cost_data['Calendar_Period']<datetime(2021,7,1)].index, inplace=True)
    return cost_data


def get_date_range(historical_cost_data):
    # st.sidebar.write("Calculating the date range of the data:")
    first_month = historical_cost_data['Calendar_Period'].min()
    end_month = pd.Period(datetime.today() + relativedelta(months=-1), freq='M').end_time.date()
    date_range = pd.date_range(start=first_month, end=end_month, freq='M').tolist()
    date_range.append("")  
    return date_range


def select_reporting_month(date_range):
    def month_change():
        st.session_state.grid_key += 1
        # st.sidebar.markdown("## Not ready for grid.")
        st.session_state.ready_for_grid = False

    # st.sidebar.write("Choose a month:")
    st.sidebar.selectbox( label = "Select a Reporting Month:",
                options = date_range,
                index = (len(date_range)-1),
                format_func=lambda x: x.strftime('%b %Y') if x!="" else x,
                key= 'reporting_month',
                on_change = month_change)
    # return datetime(2022,3,31)
    return


def select_reporting_month_from_existing(date_range):
    st.sidebar.write("Choose a month:")
    st.sidebar.selectbox( label = "Reporting Month:",
                options = date_range,
                # index = (len(date_range)-1),
                format_func=lambda x: x.strftime('%b %Y') if x!="" else x,
                key= 'reporting_month')
    return




def select_forecast_end_date():
    forecast_end_date = datetime(2022,11,15)
    return forecast_end_date


def create_cost_data_for_reporting_month(cost_estimate_data, cost_by_fiscal_period, date_range, reporting_month):
    first_month = date_range[0]
    last_month = reporting_month
    d_end=[0]*len(pd.period_range(first_month, last_month, freq='M'))
    for i in range(len(pd.period_range(first_month, last_month, freq='M'))):
            d_start=pd.Period(first_month+relativedelta(months=i), freq='M').start_time.date()
            d_end[i]=pd.Period(first_month+relativedelta(months=i), freq='M').end_time.date() 
            cost_by_fiscal_period[d_end[i].strftime('%b_%y')+'_$'] = cost_by_fiscal_period.apply(lambda x: x.Actual_Dollars if x.Calendar_Period>=d_start and x.Calendar_Period<=d_end[i] else 0, axis=1)
    cost_by_fiscal_period.drop(['Actual_Dollars','Calendar_Period'], axis=1, inplace=True)
    cost_by_fiscal_period=cost_by_fiscal_period.groupby(['Cost_Item']).apply(lambda x: x.sum())
    cost_by_fiscal_period.drop(['Cost_Item'], axis=1, inplace=True)
    # cost_by_fiscal_period['ACTD'] = cost_by_fiscal_period.sum(axis=1)
    cost_by_fiscal_period.reset_index(inplace=True)
    cost_by_fiscal_period = cost_by_fiscal_period.rename(columns = {'Cost_Item':'cost_item'})
    
    merged_data = pd.merge(cost_by_fiscal_period, cost_estimate_data, on='cost_item', how='left')
    merged_data['reporting_month'] = reporting_month
    
    cols = list(merged_data.columns.values)
    col_list = [ cols[-1], cols[-4], cols[0], cols[-3], cols[-2] ]
    col_list.extend(cols[1:-4])
    merged_data = merged_data[ col_list ]

    this_range = pd.period_range(first_month, last_month, freq='M')
    for i, item in enumerate(this_range):
        # merged_data[item.strftime('%b_%y')+'_%']=merged_data.apply(lambda x: x[item.strftime('%b_%y')+'_$']/x.EAC if x.EAC>0 else 0, axis=1)
        merged_data[item.strftime('%Y-%m')]=merged_data.apply(lambda x: x[item.strftime('%b_%y')+'_$']/x.EAC if x.EAC>0 else 0, axis=1)
        merged_data.drop([item.strftime('%b_%y')+'_$'], axis=1, inplace=True)
        
    # this_range = pd.period_range(first_month, last_month, freq='M')
    # for i, item in enumerate(this_range):
    #     if i == 0:
    #         merged_data[item.strftime('%b_%y')+'_%']=merged_data.apply(lambda x: x[item.strftime('%b_%y')+'_$']/x.EAC if x.EAC>0 else 0, axis=1)
    #     else:
    #         merged_data[this_range[i].strftime('%b_%y')+'_%'] = (
    #                         merged_data.apply(lambda x: x[this_range[i].strftime('%b_%y')+'_$']/x.EAC + x[this_range[i-1].strftime('%b_%y')+'_%'] if x.EAC>0 else 0, axis=1) 
    #                         )
    return merged_data


def monthly_forecast_calcs(x,date_range, i):
    global business_days_in_month
    start_of_current_month = date_range[i].date()
    if x['item_start_date'] <= start_of_current_month:
        business_days_in_month = np.busday_count(date_range[i].date(), date_range[i].date() + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
    if x['item_start_date'] > start_of_current_month and x['item_start_date'] < start_of_current_month + relativedelta(months=1):
        # st.write("starts this month")
        business_days_in_month = np.busday_count(x['item_start_date'], start_of_current_month + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0])
        # st.write(business_days_in_month)
    if x['item_start_date'] >= start_of_current_month + relativedelta(months=1):
        business_days_in_month = 0
    if x['days_left']>business_days_in_month:
        work_days_in_month =  business_days_in_month 
    else:
        work_days_in_month = x['days_left']
    return work_days_in_month


def get_cost_forecast_settings(cost_estimate_data, reporting_month, forecast_end_date):
    """
        EITHER GET SETTINGS FROM DATABASE TABLE OR CREATE NEW DEFAULT SETTINGS
    """
    df = pd.DataFrame(cost_estimate_data['cost_item'])
    df['reporting_month']=reporting_month
    df['item_start_date']=df['reporting_month'].apply(lambda x: pd.Period(x,freq='M').start_time + relativedelta(months=1))
    df['item_end_date']=forecast_end_date
    df['forecast_method']="Timeline"

    df['num_of_days_duration'] = df.apply(lambda x: np.busday_count(x.item_start_date.date(), x.item_end_date.date(), weekmask=[1,1,1,1,1,0,0]), axis = 1)
    df['days_left'] = df['num_of_days_duration']
    forecast_date_range = pd.period_range(reporting_month+relativedelta(months=1), forecast_end_date, freq='M').to_timestamp()
    for i in range(len(forecast_date_range)):
        col_month = forecast_date_range[i].strftime('%Y-%m')
        df['work_days_in_month']=df.apply(lambda x: monthly_forecast_calcs(x, forecast_date_range, i), axis=1)
        df['days_left'] = df['days_left'] - df['work_days_in_month']
        # df[col_month+'_BDIM']=df.apply(lambda x: np.busday_count(forecast_date_range[i].date(), forecast_date_range[i].date() + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0]), axis=1)

        df[col_month+'-F']=df.apply(lambda x: x['work_days_in_month']/x['num_of_days_duration'], axis=1)
    df.drop(['num_of_days_duration', 'days_left', 'work_days_in_month'], axis=1,inplace=True)
    # cols = list(df.columns.values)
    # col_list = [ cols[0], cols[1], cols[2], cols[3], cols[4], cols[5] ]
    # col_list.extend(cols[6:])
    # df = df[ col_list ]
    # st.write('df')
    # st.write(df.head(5))
    return df


def recalculate_cost_forecast_settings(df, reporting_month, forecast_end_date):
    df['num_of_days_duration'] = df.apply(lambda x: np.busday_count(x.item_start_date, x.item_end_date, weekmask=[1,1,1,1,1,0,0]), axis = 1)
    df['days_left'] = df['num_of_days_duration']
    forecast_date_range = pd.period_range(reporting_month+relativedelta(months=1), forecast_end_date, freq='M').to_timestamp()
    for i in range(len(forecast_date_range)):
        df['work_days_in_month']=df.apply(lambda x: monthly_forecast_calcs(x, forecast_date_range, i), axis=1)
        df['days_left'] = df['days_left'] - df['work_days_in_month']
        df[forecast_date_range[i].strftime('%b_%y')+'_F%']=df.apply(lambda x: x['work_days_in_month']/x['num_of_days_duration'], axis=1)
    df.drop(['num_of_days_duration', 'days_left', 'work_days_in_month'], axis=1,inplace=True)
    cols = list(df.columns.values)
    col_list = [ cols[0], cols[1], cols[2], cols[3], cols[4], cols[5] ]
    col_list.extend(cols[6:])
    df = df[ col_list ]
    return df


def create_cost_data_table(reporting_month_cost_data, cost_forecast_settings, start, reporting_month, forecast_end_date):
    """  Merge ACTUAL with FORECAST, calculate cumulative percentages"""
    reporting_month_cost_data.drop(['reporting_month'], axis=1, inplace=True)
    cost_data_table =  pd.merge(reporting_month_cost_data, cost_forecast_settings, on='cost_item', how='left')
    ### Cumulative 'actual' percentages
    this_range = pd.period_range(start, reporting_month, freq='M')
    for i, item in enumerate(this_range):
        if i == 0:
            cost_data_table[item.strftime('%Y-%m')+'-c']=cost_data_table.apply(lambda x: x[item.strftime('%Y-%m')], axis=1)
        else:
            cost_data_table[this_range[i].strftime('%Y-%m')+'-c'] = (
                            cost_data_table.apply(lambda x: x[this_range[i].strftime('%Y-%m')] + x[this_range[i-1].strftime('%Y-%m')+'-c'], axis=1) 
                            )
        cost_data_table['total'] = cost_data_table[this_range[i].strftime('%Y-%m')+'-c'] 

    ### Cumulative forecast percentages - setting to zero
    # forecast_range = pd.period_range(reporting_month+relativedelta(months=1), forecast_end_date, freq='M')
    # for i, item in enumerate(forecast_range):
    #     #  == "Timeline":
    #     cost_data_table[item.strftime('%Y-%m')+'-cF']=cost_data_table.apply(lambda x: 0.00 if x["forecast_method"] else 1, axis=1)

    ### Cumulative forecast percentages - calculating values
    forecast_range = pd.period_range(reporting_month+relativedelta(months=1), forecast_end_date, freq='M')
    for i, item in enumerate(forecast_range):
        if i == 0:
            cost_data_table[item.strftime('%Y-%m')+'-cF']=cost_data_table.apply(lambda x: x.total + (1-x.total)*x[item.strftime('%Y-%m')+'-F'], axis=1)
        else:
            cost_data_table[forecast_range[i].strftime('%Y-%m')+'-cF'] = (
                            cost_data_table.apply(
                                lambda x: x[forecast_range[i-1].strftime('%Y-%m')+'-cF'] + (1-x.total)*x[item.strftime('%Y-%m')+'-F'], axis=1) 
                            )
    
    # cost_data_table['reporting_month']=cost_data_table.apply(lambda x: datetime.timestamp(x['reporting_month']), axis=1)
    # cost_data_table['item_start_date']=cost_data_table.apply(lambda x: x['item_start_date'].strftime("%d/%m/%Y"), axis=1)
    # cost_data_table['item_end_date']=cost_data_table.apply(lambda x: x['item_end_date'].strftime("%d/%m/%Y"), axis=1)
    # cols = list(cost_data_table.columns.values)
    # col_list = [ cols[-4], cols[0], cols[1], cols[2], cols[3], cols[-1], cols[-3], cols[-2] ]
    # col_list.extend(cols[4:-4])
    # cost_data_table = cost_data_table[ col_list ]
    return cost_data_table



## 4
def get_whole_cost_table(table_name):
    # st.sidebar.write(f"""  4. READ table '{table_name}' from the database:  """)
    table = read_table_from_database(table_name)
    forecast_end_date = table['item_end_date'].max()

    cols = list(table.columns.values)
    date_cols = []
    for column in cols:
        try:
            datetime.strptime(column,"%Y-%m")
            date_cols.append(datetime.strptime(column,"%Y-%m"))
        except:
            pass
    
    first_month = min(date_cols)
    
    reporting_month_list = table['reporting_month'].drop_duplicates().tolist()
    return table, first_month, reporting_month_list, forecast_end_date








def display_cost_in_grid(cost_data_table, start_date, reporting_month, forecast_end_date):
    cost_data_table['reporting_month']=cost_data_table.apply(lambda x: x['reporting_month'].strftime("%b %Y"), axis=1)
    cost_data_table['item_start_date']=cost_data_table.apply(lambda x: x['item_start_date'].strftime("%d/%m/%Y"), axis=1)
    cost_data_table['item_end_date']=cost_data_table.apply(lambda x: x['item_end_date'].strftime("%d/%m/%Y"), axis=1)
    
    # st.write('cost_data_table being used in table')
    # st.write(cost_data_table)
    # st.write(f"Start date: {start_date}, Reporting month: {reporting_month}, Forecast end date: {forecast_end_date}")

    actual_children = config_actual_cost_children(start_date, reporting_month)
    forecast_children = config_forecast_cost_children(reporting_month+relativedelta(months=1), forecast_end_date)
    grid_options = configure_cost_grid_options(actual_children, forecast_children)

    
    grid_response = AgGrid(
                dataframe = cost_data_table,
                gridOptions = grid_options, 
                height = 350,
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                key = st.session_state.grid_key,
                reload_data=False,  
                data_return_mode='AS_INPUT',
                # update_mode='VALUE_CHANGED',   ## default
                update_mode='MODEL_CHANGED',
                allow_unsafe_jscode=True,
                theme="light"
    )
    
    return grid_response


## 1
def get_company():
    st.sidebar.write("1. Getting cost data...")
    cost_by_fiscal_period = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
    company_list = cost_by_fiscal_period['Company_Code'].drop_duplicates().tolist()
    company_list.append("")
    st.sidebar.selectbox(label = "Choose Company:",
                        index = (len(company_list)-1),   ## sometimes we seem to need this??
                        options = company_list,
                        key ='company' 
                        )
    if st.session_state.company != '':
        costs_for_company = cost_by_fiscal_period[cost_by_fiscal_period['Company_Code']==st.session_state.company]
        st.sidebar.write(f'1. Have current cost data for company: {st.session_state.company}')
        return st.session_state.company, costs_for_company
    else:
        return '', 0

## 2
def get_job(costs_for_company):
    st.sidebar.write(f"2. Getting a list of Jobs for company '{st.session_state.company}'...")
    job_list = costs_for_company['Job_Number'].drop_duplicates().tolist()
    job_list.append("")
    # st.session_state.job = ""
    # st.sidebar.write(f"Job: {st.session_state.job}")
    st.sidebar.selectbox(label = "Choose Job:",
                        index = (len(job_list)-1),   ## sometimes we seem to need this??
                        options = job_list,
                        key = 'job')
    if st.session_state.job != '':
        costs_for_job = costs_for_company[costs_for_company['Job_Number']==st.session_state.job]
        # st.write(f"Costs for job: {st.session_state.job}")
        # st.write(costs_for_job)
        st.sidebar.write(f'2. Have cost data for job: {st.session_state.job}')
        return st.session_state.job, costs_for_job
    else:
        return '', 0

## 3
def check_for_database_table(table_name):
    # st.sidebar.markdown("###### Checking if report data exists...")
    table_list = table_names().table_name.tolist()
    # st.write(table_list)
    if table_name in table_list:
        # st.sidebar.markdown("### Job data table exists.")
        return True
    else:
        # st.sidebar.markdown("### Job data table does not exist.")
        return False
