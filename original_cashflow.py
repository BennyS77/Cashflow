import streamlit as st
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cashflow_jscode import js

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="auto" #"collapsed" #auto
)

if 'allCostData' not in st.session_state:
    st.write("still zero 1")
    st.session_state.allCostData = []

if 'grid_data' not in st.session_state:
    st.write("starting from scratch")

    @st.experimental_memo()
    def getData():
        dataset = 'JobCostSummaryByFiscalPeriods' #'ARPostedInvoices'  #
        URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/'+dataset+'/?$format=json'
        # URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/?$format=json'
        username='317016\BenStewart' #'321076\ReportsAPI'
        password='gXAd5P6EYS5EMAdk'  #'ZdP9jZ5asd8BeSP5'
        response = requests.get(URL, auth = (username,password))
        # st.write(response.status_code)
        dict_1 = response.json()  ## create a dictionary 2 keys - 'odata.metadata' and 'value'.  Value is a list of dictionaries
        list_1 = dict_1['value']
        df_1 = pd.DataFrame(list_1)
        return df_1

    st.session_state.allCostData = getData()

    project_code = 'PD140479'
    startDate = '5/1/2021'
    endDate = '20/2/2022'
    numMonths=14
    forecastMonths=3
    startDate_obj = datetime.strptime(startDate, '%d/%m/%Y')
    endDate_obj = datetime.strptime(endDate, '%d/%m/%Y')

    costData = st.session_state.allCostData[st.session_state.allCostData['Job_Number']==project_code]
    costData = costData[[ 'Cost_Item','Actual_Dollars','Fiscal_Period']]
    costData.Fiscal_Period = pd.to_datetime(costData.Fiscal_Period, format='%Y-%m')
    costData['Actual_Dollars']=costData['Actual_Dollars'].astype(float)
    costData.Fiscal_Period = costData.Fiscal_Period.apply(lambda x: x.date())   # converts timestamps to datetime
    costData['new_date'] = costData.Fiscal_Period.apply(lambda x: x - relativedelta(months=6)+relativedelta(days=15))   # converts timestamps to datetime

    d_end=[0]*numMonths

    for i in range(numMonths):
        d_start=pd.Period(startDate_obj,freq='M').start_time.date() + relativedelta(months=i)
        d_end[i]=pd.Period(startDate_obj,freq='M').end_time.date() + relativedelta(months=i)
        costData[d_end[i].strftime('%d-%m-%y')+' $'] = costData.apply(lambda x: x.Actual_Dollars if x.new_date>=d_start and x.new_date<=d_end[i] else 0, axis=1)

    costData_dropped=costData.drop(['Fiscal_Period','Actual_Dollars','new_date'], axis=1)

    groupedCostData=costData_dropped.groupby(['Cost_Item']).apply(lambda x: x.sum())
    groupedCostData=groupedCostData.drop(['Cost_Item'], axis=1)
    groupedCostData['ACTD'] = groupedCostData.sum(axis=1)

    eacData= pd.read_csv('CostAtCompletion.csv')
    eacData=eacData[['Cost Item','Desc','Estimate At Completion']]
    eacData = eacData.rename(columns={'Cost Item':'Cost_Item','Estimate At Completion':'EAC'})

    st.session_state.grid_data = pd.merge(groupedCostData, eacData,on='Cost_Item', how='inner')

    for i in range(numMonths):
        st.session_state.grid_data[d_end[i].strftime('%d-%m-%y')+' %']=st.session_state.grid_data.apply(lambda x: x[d_end[i].strftime('%d-%m-%y')+' $']/x.EAC if x.EAC>0 else 0, axis=1)

    st.session_state.grid_data['ETC']=st.session_state.grid_data['EAC']-st.session_state.grid_data['ACTD']
    st.session_state.grid_data['forecastMethod']='Timeline'
    st.session_state.grid_data['startDate']=startDate
    st.session_state.grid_data['endDate']=endDate
else:
    st.write('Using session state')


st.session_state.grid_data['forecast1']=st.session_state.grid_data.apply(lambda x: x.ETC/forecastMonths if x.forecastMethod=='Timeline' else x.ETC/forecastMonths/2, axis =1)
st.session_state.grid_data['f1_%']=st.session_state.grid_data.apply(lambda x: x.forecast1 if x.forecastMethod=='Timeline' else x.ETC/forecastMonths/2, axis =1)
st.session_state.grid_data['forecast2']=st.session_state.grid_data.apply(lambda x: x.ETC/forecastMonths/2 if x.forecastMethod=='Timeline' else x.ETC/forecastMonths, axis =1)
st.session_state.grid_data['forecast3']=st.session_state.grid_data.apply(lambda x: x.ETC-x.forecast1-x.forecast2 if x.forecastMethod=='Timeline' else 0, axis =1)

st.write(st.session_state.grid_data.head(3))

rowDataDict={"EAC":st.session_state.grid_data['EAC'].sum(),"ACTD":st.session_state.grid_data['ACTD'].sum(),"ETC":st.session_state.grid_data['ETC'].sum(),"Tot":"Total:"}
for i in range(numMonths):
  dollar_key=d_end[i].strftime('%d-%m-%y')+' $'
  percent_key=d_end[i].strftime('%d-%m-%y')+' %'
  rowDataDict.update({dollar_key:st.session_state.grid_data[d_end[i].strftime('%d-%m-%y')+' $'].sum()})
  rowDataDict.update({percent_key:st.session_state.grid_data[d_end[i].strftime('%d-%m-%y')+' $'].sum()/st.session_state.grid_data['EAC'].sum()})

pinnedRowData=[rowDataDict]

actualChildren=[{"headerName":"","field":"Tot","minWidth":80}]

for i in range(0,numMonths,1):
    month=d_end[i].strftime('%b %Y')
    monthly_dollars = d_end[i].strftime('%d-%m-%y')+' $'
    monthly_percent = d_end[i].strftime('%d-%m-%y')+' %'
    actualChildren.append(
        {"headerName" : month+' - Claim '+str(i+1),
        'columnGroupShow': 'open',
         "children":[
            { 'field': monthly_dollars,
              'headerName' : ' $',
              'maxWidth':80,
              'suppressMenu':True,
              "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
              'cellStyle':{'backgroundColor':'lightgrey'}
              },
            { 'field': monthly_percent,
              'headerName' : ' %',
              'maxWidth':60,
              'suppressMenu':True,
              "valueFormatter": "parseFloat(value*100).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
              'cellStyle':{'backgroundColor':'lightgrey'} }
            ]},
  )

forecastChildren=[{"headerName":"","field":"for","minWidth":100}]

for i in range(0,forecastMonths,1):
    month= 'Month: '+str(i)
    forecast_dollars = 'F $'
    forecast_percent = 'F %'
    forecastChildren.append(
        {"headerName" : month+' - Claim '+str(i+1),
        'columnGroupShow': 'open',
         "children":[
            { 'field': forecast_dollars+str(i),
              'headerName' : ' $',
              'maxWidth':80,
              'suppressMenu':True,
              # "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
              # 'cellStyle':{'backgroundColor':'lightgrey'}
              },
            { 'field': forecast_percent+str(i),
              'headerName' : ' %',
              'maxWidth':60,
              'suppressMenu':True,
              # "valueFormatter": "parseFloat(value*100).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
              # 'cellStyle':{'backgroundColor':'lightgrey'}
              }
            ]},
  )



topGridOptions={
  "defaultColDef": {
    "minWidth": 50,
    "maxWidth": 100,
    "editable": True,
    "filter": True,
    "resizable": True,
    "sortable": True
  },
  "columnDefs": [
    { "headerName": "Cost Item",
      "field": "Cost_Item",
      # "type": [],
    #   "maxWidth": 100
    },
    { "headerName": "Description",
      "field": "Desc",
      "type": [],
      # "width": 400
    },
    { "headerName": "EAC",
      "field": "EAC",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "ACTD",
      "field": "ACTD",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(data.ACTD).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "ETC",
      "field": "ETC",
      "type": [
        "numericColumn",
        "numberColumnFilter"
        ],
      "valueFormatter": "parseFloat(data.ETC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
    },
    { "headerName": "Forecast Method",
      "field": "forecastMethod",
      "type": [],
      "editable": True,
      # "maxWidth": 140,
      "cellEditor": 'agRichSelectCellEditor',
      "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
    },
    { "headerName": "Start Date",
      "field": "startDate",
      "type": [],
      "editable": True
    },
    { "headerName": "End Date",
      "field": "endDate",
      "type": [],
      "editable": True
    },
    { "headerName": "Actual",
      "field": "Actual",
      "children":actualChildren
    },
    { "headerName": "Forecast",
      "field": "Forecast",
      "children":forecastChildren
    },
    
     
    
  ],
  # "rowSelection": "multiple",
#   "rowMultiSelectWithClick": true,
#   "suppressRowDeselection": false,
#   "suppressRowClickSelection": false,
#   "groupSelectsChildren": true,
#   "groupSelectsFiltered": true,
  "onCellValueChanged": js,
  # "suppressAutoSize": 'true',
  # "animateRows": 'true',

  "pinnedTopRowData":pinnedRowData,
  "debug":True,
#   "groupIncludeTotalFooter": true
}

# cost_merge=st.session_state.grid_response['data']

topGridHeight = 300
# st.dataframe(cost_merge.head(5))
st.markdown('### Cashflow Forecast')
# st.markdown('####')
grid_response = AgGrid(
        dataframe = st.session_state.grid_data,
        gridOptions = topGridOptions, 
        height = topGridHeight,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=False,
        key = 'top',
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
        )


### nothing below here happens before the grid is rerendered after a cell edit

# df = st.session_state.grid_response['data']

if len(grid_response['data'].compare(st.session_state.grid_data))>0:
  diff = grid_response['data'].compare(st.session_state.grid_data)
  col_changed=list(diff.columns[0])[0]
  row_changed=diff.index[0]
  st.write(diff)
  st.write(col_changed)
  st.write(row_changed)
  # st.experimental_rerun()


def update_data():
  update_button = False

update_button = st.button('update')
        
if update_button:
  st.write("button clicked")
else:
  st.write("button NOT clicked")



st.markdown('#')

if st.button('Clear cached data'):
        st.experimental_memo.clear()



