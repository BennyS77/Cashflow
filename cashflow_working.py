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
    # st.write(d_end[i])
    costData[d_end[i].strftime('%d-%m-%y')+' $'] = costData.apply(lambda x: x.Actual_Dollars if x.new_date>=d_start and x.new_date<=d_end[i] else 0, axis=1)
    # costData['Percent'+str(i)] = costData.apply(lambda x: x.Actual_Dollars if x.new_date>=d_start and x.new_date<=d_end else 0, axis=1)

costData_dropped=costData.drop(['Fiscal_Period','Actual_Dollars','new_date'], axis=1)

groupedCostData=costData_dropped.groupby(['Cost_Item']).apply(lambda x: x.sum())
groupedCostData=groupedCostData.drop(['Cost_Item'], axis=1)
groupedCostData['ACTD'] = groupedCostData.sum(axis=1)

# groupedCostData=groupedCostData.droplevel(level=1, axis=1)
# groupedCostData.reset_index(level=0, inplace=True)
# groupedCostData = costData.groupby(['Cost_Item']).agg({'Full_Ret':['sum'],'Open_Retention':['sum'],'Ret_Deducted':['sum'],'Ret_Paid':['sum'],'End_Ret':['sum']})

#     df_1['Subtotal']=df_1['Subtotal'].astype(float)
# st.write(type(costData.Fiscal_Period.iloc[0]))

# st.write(costData)
# st.write(costData_dropped)
# st.write('grouped')
# st.write(groupedCostData)



eacData= pd.read_csv('CostAtCompletion.csv')
eacData=eacData[['Cost Item','Desc','Estimate At Completion']]
eacData = eacData.rename(columns={'Cost Item':'Cost_Item','Estimate At Completion':'EAC'})

# st.write('eacData')
# st.write(eacData)

# cost_merge = pd.merge(costData, eacData,on='Cost_Item', how='inner')
cost_merge = pd.merge(groupedCostData, eacData,on='Cost_Item', how='inner')
cost_merge['ETC']=cost_merge['EAC']-cost_merge['ACTD']
cost_merge['forecastMethod']='Timeline'
cost_merge['startDate']=startDate
cost_merge['endDate']=endDate
cost_merge['forecast1']=cost_merge['EAC']-cost_merge['ACTD']
cost_merge['forecast2']=cost_merge['EAC']-cost_merge['ACTD']-cost_merge['forecast1']
cost_merge['forecast3']=cost_merge['EAC']-cost_merge['ACTD']-cost_merge['forecast1']-cost_merge['forecast2']
# columns=list(cost_merge.columns)
# month_column=columns[1:-7]
# st.write(month_column)
# cost_merge = cost_merge[['Cost_Item','Desc','EAC','ACTD','ETC','forecastMethod','startDate','endDate']+month_column]
# st.write('merged')
# st.write(cost_merge)



js = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let col_changed = e.column.colId;
    test = rowIndex;
    console.log(api, test, col_changed);
    let rowNode = api.getDisplayedRowAtIndex(rowIndex);
    api.flashCells({
        rowNodes: [rowNode],
        columns: [col_changed],
        flashDelay: 250
        });
    };
    """)

myChildren=[{'field': d_end[0].strftime('%d-%m-%y')+' $', 'width':100, 'cellStyle':{'backgroundColor':'lightgrey'}}]
for i in range(1,numMonths,1):
    myField=d_end[i].strftime('%d-%m-%y')+' $'
    col={'field': myField,'columnGroupShow':'open', 'width':100, 'cellStyle':{'backgroundColor':'lightgrey'}}
    myChildren.append(col)

# st.write(myChildren)

my_go={
  "defaultColDef": {
    "minWidth": 50,
    "editable": 'false',
    "filter": True,
    "resizable": True,
    "sortable": True,
    "maxWidth": 120
  },
  "columnDefs": [
    { "headerName": "Cost Item",
      "field": "Cost_Item",
      "type": [],
    #   "maxWidth": 100
    },
    { "headerName": "Description",
      "field": "Desc",
      "type": [],
      "width": 400
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
      "maxWidth": 140,
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
      "children": myChildren
    },
    { "headerName": "Forecast Month-1",
      "field": "forecast1",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(data.forecast1).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
      "maxWidth": 180,
      "editable": True
    },
    { "headerName": "Forecast Month-2",
      "field": "forecast2",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(data.ETC-data.forecast1).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
      "maxWidth": 180,
      "editable": True
    },
    { "headerName": "Forecast Month-3",
      "field": "forecast3",
      "type": [
        "numericColumn",
        "numberColumnFilter"
      ],
      "valueFormatter": "parseFloat(data.forecast3).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
      "maxWidth": 180,
      "editable": True
    }
  ],
  "rowSelection": "multiple",
#   "rowMultiSelectWithClick": true,
#   "suppressRowDeselection": false,
#   "suppressRowClickSelection": false,
#   "groupSelectsChildren": true,
#   "groupSelectsFiltered": true,
  "onCellValueChanged": "<st_aggrid.shared.JsCode object at 0x7f73a3643e80>",
  "suppressAutoSize": 'true',
  "animateRows": 'true',
#   "groupIncludeTotalFooter": true
}



grid_height = 500

st.markdown('## Cashflow Forecast')
st.markdown('####')
grid_response = AgGrid(
        cost_merge,
        gridOptions = my_go, 
        height = grid_height,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=False,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED',
        allow_unsafe_jscode=True #Set it to True to allow jsfunction to be injected
        )



df = grid_response['data']
# st.write(df)
selected = grid_response['selected_rows']
selected_df=pd.DataFrame(selected)
# st.write(selected_df)

st.markdown('#')

if st.button('Clear cached data'):
        st.experimental_memo.clear()



