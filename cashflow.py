import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid, JsCode
import requests
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(
     page_title="Premier Reports - Cashflow Report",
     page_icon="bar-chart",
     layout="wide",
     initial_sidebar_state="auto" #"collapsed" #auto
)

if 'allCostData' not in st.session_state:
    st.session_state.allCostData = []

dropdown_jscode = JsCode("""
  function cellEditorSelector(params) {
    return {
      component: 'agRichSelectCellEditor',
      params: {
        values: ['Timeline', 'Manual','S-curve'],
      },
    };
  };
  """)


@st.experimental_memo()
def getData():
    dataset = 'JobCostSummaryByFiscalPeriods' #'ARPostedInvoices'  #
    URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/'+dataset+'/?$format=json'
    # URL = 'https://reporting.jonas-premier.com/OData/ODataService.svc/?$format=json'
    username='317016\BenStewart' #'321076\ReportsAPI'
    password='Qwerty123456'  #'ZdP9jZ5asd8BeSP5'
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

cost_merge = pd.merge(groupedCostData, eacData,on='Cost_Item', how='inner')

for i in range(numMonths):
    cost_merge[d_end[i].strftime('%d-%m-%y')+' %']=cost_merge.apply(lambda x: x[d_end[i].strftime('%d-%m-%y')+' $']/x.EAC if x.EAC>0 else 0, axis=1)

cost_merge['ETC']=cost_merge['EAC']-cost_merge['ACTD']
cost_merge['forecastMethod']='Timeline'
cost_merge['startDate']=startDate
cost_merge['endDate']=endDate
cost_merge['forecast1']=cost_merge['EAC']-cost_merge['ACTD']
cost_merge['forecast2']=cost_merge['EAC']-cost_merge['ACTD']-cost_merge['forecast1']
cost_merge['forecast3']=cost_merge['EAC']-cost_merge['ACTD']-cost_merge['forecast1']-cost_merge['forecast2']
# st.write(cost_merge)

js = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let col_changed = e.column.colId;
    console.log(api, rowIndex, col_changed);
    let rowNode = api.getDisplayedRowAtIndex(rowIndex);
    api.flashCells({
        rowNodes: [rowNode],
        columns: [col_changed],
        flashDelay: 250
        });
    };
    """)
EAC_vf = JsCode("""
  function(params) {
    if (params.node.rowPinned === 'top') {
        return parseFloat(params.data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
    } else {
       return parseFloat(params.data.EAC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
    }
  };
  """)
ACTD_vf = JsCode("""
  function(params) {
    if (params.node.rowPinned === 'top') {
        return ""
    } else {
       return parseFloat(params.data.ACTD).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
    }
  };
  """)
ETC_vf = JsCode("""
  function(params) {
    if (params.node.rowPinned === 'top') {
        return ""
    } else {
       return parseFloat(params.data.ETC).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
    }
  };
  """)


rowDataDict={"EAC":cost_merge['EAC'].sum(),"ACTD":cost_merge['ACTD'].sum(),"ETC":cost_merge['ETC'].sum(),"Tot":"Total:"}
for i in range(numMonths):
  dollar_key=d_end[i].strftime('%d-%m-%y')+' $'
  percent_key=d_end[i].strftime('%d-%m-%y')+' %'
  rowDataDict.update({dollar_key:cost_merge[d_end[i].strftime('%d-%m-%y')+' $'].sum()})
  rowDataDict.update({percent_key:cost_merge[d_end[i].strftime('%d-%m-%y')+' $'].sum()/cost_merge['EAC'].sum()})

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

forecastChildren=[
    { 'field': '$' },
    { 'field': '%' }
]

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
      "children":[
        {"headerName":'Feb-22, Claim 7',
         "children":forecastChildren},
        {"headerName":'Mar-22, Claim 8',
        "children":forecastChildren},
        {"headerName":'Apr-22, Claim 9',
        "children":forecastChildren}
                ]
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


### Ag-grid
### Server-side records Operations

topGridHeight = 500

st.markdown('## Cashflow Forecast')
st.markdown('####')
grid_response_top = AgGrid(
        cost_merge,
        gridOptions = topGridOptions, 
        height = topGridHeight,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=False,
        key = 'top',
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
        )



# df = grid_response['data']
# # st.write(df)
# selected = grid_response['selected_rows']
# selected_df=pd.DataFrame(selected)
# st.write(selected_df)

st.markdown('#')

if st.button('Clear cached data'):
        st.experimental_memo.clear()



