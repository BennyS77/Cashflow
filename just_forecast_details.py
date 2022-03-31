from queue import Empty
import streamlit as st
import pandas as pd
from my_config import pageConfig, setSessionData, setLogIn
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cost_data import createForecastDetails, forecast_calcs, getJobCostByFiscalPeriod, getEACdata, filterFormatData, calc_cost_per_month_and_ACTD
from cost_data import merge_eac_and_calc_percent, forecast_calcs
from st_aggrid import AgGrid, JsCode
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions

pageConfig()

if 'table_1' not in st.session_state:
    st.session_state.table_1 = []
if 'table_1_exists' not in st.session_state:
    st.session_state.table_1_exists = False
if 'grid_key' not in st.session_state:
    st.session_state.grid_key = 0

creds, submit_button = setLogIn()


company = 'G01'
job = 'PD140479'

all_jobs_cost_by_fiscal_period = getJobCostByFiscalPeriod(creds)
eac_data = getEACdata()
# st.write(eac_data)
cost_by_fiscal_period, date_range = filterFormatData(company, job, all_jobs_cost_by_fiscal_period)
index = date_range.index(pd.Period(datetime.today(),freq='M').end_time.date() + relativedelta(months=-1))
# st.write('cost_by_fiscal_period')
# st.write(cost_by_fiscal_period)

def report_change():
    st.session_state.grid_key = st.session_state.grid_key + 1

forecast_end_date = st.sidebar.date_input(
    "forecast end date",
    (datetime.today() + relativedelta(months=6)).date(),
    on_change = report_change
    )
reporting_month = st.sidebar.selectbox(
    "Reporting month:",
    date_range,
    index = index,
    format_func=lambda x: x.strftime('%b %Y'),
    key="reportingmonth",
    on_change = report_change
    )

cost_with_ACTD = calc_cost_per_month_and_ACTD(cost_by_fiscal_period, date_range[0], reporting_month)
# st.write('cost_with_ACTD')
# st.write(cost_with_ACTD)

cost_data = merge_eac_and_calc_percent(cost_with_ACTD, eac_data, date_range[0], reporting_month)
# st.write('Actual cost data:')
# st.write(cost_data)


if st.session_state.table_1_exists == False:
    # st.write(" !! New Job !!  Database table does not exist. Creating....")
    st.session_state.table_1 = createForecastDetails(eac_data.cost_item, reporting_month, forecast_end_date)
    st.session_state.table_1_exists = True

# st.write('st.session_state.table_1')
# st.write(st.session_state.table_1)


forecast_data_for_reporting_month = st.session_state.table_1.loc[st.session_state.table_1['reporting_month'] == reporting_month.date()]
    

if len(forecast_data_for_reporting_month) > 0:
    # st.write("Data for the reporting month exists")
    if forecast_data_for_reporting_month['forecast_end_date'].iloc[0] != forecast_end_date:
        # st.write("forecast end date is different.")
        append_table = createForecastDetails({'cost_item':['test']}, reporting_month, forecast_end_date)
        st.session_state.table_1 = st.session_state.table_1.append(append_table)
        st.session_state.table_1 = st.session_state.table_1[st.session_state.table_1.cost_item != 'test']
else:
    # st.write("No data for selected reporting month. Creating... ")
    table_2 = createForecastDetails(eac_data.cost_item, reporting_month, forecast_end_date)
    st.session_state.table_1 = st.session_state.table_1.append(table_2)


# st.write("The data available in the 'database'")
# st.write(st.session_state.table_1)
forecast_data_for_reporting_month = st.session_state.table_1.loc[st.session_state.table_1['reporting_month'] == reporting_month.date()]
# st.write("Forecast data for reporting month...")
# st.write(cost_data)
# st.write(forecast_data_for_reporting_month)


cost_display_data = forecast_calcs(cost_data, forecast_data_for_reporting_month)
# st.write(cost_display_data)


rowDataDict={"autoGroup":"Total Costs:","EAC":cost_display_data['EAC'].sum(),"ACTD":cost_display_data['ACTD'].sum(),"ETC":cost_display_data['ETC'].sum()}

my_range = pd.date_range(start=date_range[0], end=reporting_month, freq='M').tolist()

for i, item in enumerate(my_range):
    # st.write(item)
    rowDataDict.update({item.strftime('%b_%y')+'_$':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum())})
    rowDataDict.update({item.strftime('%b_%y')+'_%':float(cost_display_data[item.strftime('%b_%y')+'_$'].sum()/cost_display_data['EAC'].sum())})

forecast_date_range = pd.date_range(start = reporting_month+relativedelta(months=1), end = forecast_end_date+relativedelta(months=1), freq='M').tolist()
for i, item in enumerate(forecast_date_range):
    # st.write(item)
    rowDataDict.update({item.strftime('%b_%y')+'_F$':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum())})
    rowDataDict.update({item.strftime('%b_%y')+'_F%':float(cost_display_data[item.strftime('%b_%y')+'_F$'].sum()/cost_display_data['EAC'].sum())})

pinnedRowData=[rowDataDict]



actual_children = configActualChildren(date_range[0], reporting_month)
forecast_children = configForecastChildren(reporting_month, forecast_end_date)
gridOptions, custom_css = configureGridOptions(actual_children, forecast_children, pinnedRowData)

st.markdown("# Cost Forecast")

grid_response = AgGrid(
      dataframe = cost_display_data,
      custom_css = custom_css,
      gridOptions = gridOptions, 
      height = 600,
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

# diff = grid_response['data'].compare(cost_display_data)
# # st.write(diff)
# # diff = diff.drop(['reporting_month','forecast_end_date','current_month'], axis=1)
# # non_nan = diff['forecast_method','self'].isna()
# non_nan = diff['forecast_method','self'].dropna(axis=0)
# index_value = non_nan.index.tolist()
# # st.write(index_value[0])

# st.session_state.table_1['forecast_method'].iloc[index_value[0]] = "Manual"
# # st.write("session state table")
# # st.write(st.session_state.table_1['forecast_method'])


# st.button('button')
# st.write(pd.isnull(diff).any(1))
# st.write(type(diff.iloc[0,3]))
# st.write(diff.iloc[0,3])
# st.write(diff.dtypes)
# diff.info(verbose=True)
# st.write(diff['forecast_method', 'self'])