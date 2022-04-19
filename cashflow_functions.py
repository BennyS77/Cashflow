import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid
from aggrid_functions_cost import config_actual_cost_children, config_forecast_cost_children, configure_cost_grid_options


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
    def login_form(credentials):
        st.session_state.creds = credentials
        st.session_state.login_confirmed = True
        return

    st.sidebar.markdown("# ")
    st.sidebar.markdown("## Login")
    with st.sidebar.form('credentials', clear_on_submit=True):
        client_id = st.text_input('Client ID:', 'test client') 
        username = st.text_input('Username:','test username')  
        password = st.text_input('Password:',type="password") 
        client_id = '317016'
        username = 'BenStewart'
        password = 'Woerifjoi439856'
        creds_dict = {"username":client_id+'\\'+username, "password":password}
        st.form_submit_button('Submit', kwargs = dict(credentials = creds_dict), on_click = login_form)
    return



@st.experimental_memo()
def fetch_Odata(dataset, columns='*', filter=""):
    URL = "https://reporting.jonas-premier.com/OData/ODataService.svc/"+dataset
    query = "?$filter="+filter + "&$select="+columns + "&$format=json"
    user_auth = ('317016\BenStewart','Woerifjoi439856')
    response = requests.get(URL+query, auth = user_auth)
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
    return df_1


def get_all_cost_data(company, job):
    cost_data = fetch_Odata(
            dataset = 'JobCostSummaryByFiscalPeriods', 
            columns = "Company_Code,Job_Number,Fiscal_Period,Cost_Item,Actual_Dollars")
    cost_data = cost_data[cost_data['Company_Code']==company]
    cost_data = cost_data[cost_data['Job_Number']==job]
    cost_data = cost_data[['Cost_Item','Actual_Dollars','Fiscal_Period']]
    cost_data['Fiscal_Period'] = pd.to_datetime(cost_data['Fiscal_Period'], format='%Y-%m')
    cost_data['Actual_Dollars']=cost_data['Actual_Dollars'].astype(float)
    cost_data['Calendar_Period'] = cost_data['Fiscal_Period'].apply(lambda x: x-relativedelta(months=6)+relativedelta(days=15))
    cost_data.drop(['Fiscal_Period'], axis=1, inplace=True)
    cost_data.drop(cost_data[cost_data['Calendar_Period']<datetime(2021,7,1)].index, inplace=True)
    return cost_data


def get_date_range(historical_cost_data):
    first_month = historical_cost_data['Calendar_Period'].min()
    end_month = pd.Period(datetime.today() + relativedelta(months=-1), freq='M').end_time.date()
    date_range = pd.date_range(start=first_month, end=end_month, freq='M').tolist()
    date_range.append("")  
    return date_range


def select_reporting_month(date_range):
    # st.sidebar.selectbox( label = "Reporting Month:",
    #             options = date_range,
    #             # index = (len(date_range)-1),
    #             format_func=lambda x: x.strftime('%b %Y') if x!="" else x,
    #             key= 'reporting_month')
    return datetime(2022,3,31)


def select_forecast_end_date():
    forecast_end_date = datetime(2022,11,11)
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
    df['reporting_month']=reporting_month.date()
    df['item_start_date']=df['reporting_month'].apply(lambda x: pd.Period(x,freq='M').start_time.date() + relativedelta(months=1))
    df['item_end_date']=forecast_end_date.date()
    df['forecast_method']="Timeline"

    df['num_of_days_duration'] = df.apply(lambda x: np.busday_count(x.item_start_date, x.item_end_date, weekmask=[1,1,1,1,1,0,0]), axis = 1)
    df['days_left'] = df['num_of_days_duration']
    forecast_date_range = pd.period_range(reporting_month+relativedelta(months=1), forecast_end_date, freq='M').to_timestamp()
    for i in range(len(forecast_date_range)):
        col_month = forecast_date_range[i].strftime('%Y-%m')
        df['work_days_in_month']=df.apply(lambda x: monthly_forecast_calcs(x, forecast_date_range, i), axis=1)
        df['days_left'] = df['days_left'] - df['work_days_in_month']
        # df[col_month+'_BDIM']=df.apply(lambda x: np.busday_count(forecast_date_range[i].date(), forecast_date_range[i].date() + relativedelta(months=1) , weekmask=[1,1,1,1,1,0,0]), axis=1)

        df[col_month+'-F']=df.apply(lambda x: x['work_days_in_month']/x['num_of_days_duration'], axis=1)
    # df.drop(['num_of_days_duration', 'days_left', 'work_days_in_month'], axis=1,inplace=True)
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
    
    cost_data_table['reporting_month']=cost_data_table.apply(lambda x: x['reporting_month'].strftime("%b %Y"), axis=1)
    # cost_data_table['item_start_date']=cost_data_table.apply(lambda x: x['item_start_date'].strftime("%d/%m/%Y"), axis=1)
    # cost_data_table['item_end_date']=cost_data_table.apply(lambda x: x['item_end_date'].strftime("%d/%m/%Y"), axis=1)
    # cols = list(cost_data_table.columns.values)
    # col_list = [ cols[-4], cols[0], cols[1], cols[2], cols[3], cols[-1], cols[-3], cols[-2] ]
    # col_list.extend(cols[4:-4])
    # cost_data_table = cost_data_table[ col_list ]
    return cost_data_table


def display_cost_in_grid(cost_data_table, start_date, reporting_month, forecast_end_date):
    actual_children = config_actual_cost_children(start_date, reporting_month)
    forecast_children = config_forecast_cost_children(reporting_month+relativedelta(months=1), forecast_end_date)
    grid_options = configure_cost_grid_options(actual_children, forecast_children)

    # st.write('cost_data_table - before')
    # st.write(cost_data_table)
    # st.write(cost_data_table.iloc[:5,13:])

    grid_response = AgGrid(
                dataframe = cost_data_table,
                gridOptions = grid_options, 
                height = 350,
                enable_enterprise_modules=True,
                fit_columns_on_grid_load=True,
                key = st.session_state.grid_key,   #- set a key to stop the grid reinitialising when the dataframe changes
                # reload_data=True,  
                reload_data=False,  
                data_return_mode='AS_INPUT',
                #   data_return_mode='FILTERED',
                # update_mode='VALUE_CHANGED',   ## default
                update_mode='MODEL_CHANGED',
                # update_mode='MANUAL',
                allow_unsafe_jscode=True,
                theme="light"
    )
    
    return grid_response



def get_company():
    return "G01"

def get_job():
    return "PD140479"

