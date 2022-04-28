import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
from cashflow_jscode import js_changed, js_clicked, row_height, col_span
from jscode import date_getter, my_setter, date_setter, forecast_amount_getter, forecast_field_formatter, amount_formatter, percent_formatter, forecast_amount_vgetter
from jscode import value_getter, forecast_percent_vgetter, editable, date_editable, value_formatter, actual_amount_vgetter, actual_percent_vgetter, actual_percent_vformatter

def config_actual_cost_children(firstMonth, lastMonth):
    actual_children=[{ 
        'headerName': '%',
        'colId':'ACTD_percent',
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        'minWidth': 60,
        'maxWidth': 60,
        # "aggFunc": "sum",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
    
        # "cellClass": 'ag-right-aligned-cell',
        "valueGetter": actual_percent_vgetter,
        "valueFormatter": actual_percent_vformatter
      },
      {
        'headerName': '$',
        'colId':'ACTD_amount',
        'columnGroupShow': 'closed',
        # 'suppressMenu':True,
        'minWidth': 70,
        'maxWidth': 100,
        "aggFunc": "sum",
        "type": [
                "numericColumn",
                "numberColumnFilter"
        ],
        # "cellClass": 'ag-right-aligned-cell',
        "valueGetter": actual_amount_vgetter,
        "valueFormatter":value_formatter
      }
      ]
    for i, item in enumerate(pd.period_range(firstMonth, lastMonth, freq='M')):
        column_id = item.strftime('%Y-%m')
        header_month = item.strftime('%b %Y')
        actual_children.append(
            {
                "headerName" : header_month,
                'columnGroupShow': 'open',
                "children":[
                    {
                        'field': column_id+'-c',
                        'headerName' : ' % ',
                        "type": [
                              "numericColumn",
                              "numberColumnFilter"
                        ],
                        'minWidth': 60,
                        'maxWidth': 60,
                        'suppressMenu':True,
                        "valueFormatter": percent_formatter,
                    },
                    {
                        'headerName' : ' $ ',
                        'colId': column_id+'-$',
                        "type": [
                              "numericColumn",
                              "numberColumnFilter"
                        ],
                        "aggFunc": "sum",
                        'minWidth': 70,
                        'maxWidth': 80,
                        'suppressMenu':True,
                        "valueGetter": value_getter,
                        'valueFormatter':value_formatter
                    },
                ]
            },
        )
    return actual_children



def config_forecast_cost_children(report_date, end_date):
    forecast_children=[{
        'headerName': '%',
        'colId':'ETC_percent',
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        'minWidth': 60,
        'maxWidth': 60,
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
    
        # "cellClass": 'ag-right-aligned-cell',
        'valueGetter':forecast_percent_vgetter,
        "valueFormatter": actual_percent_vformatter
        },
        {
        'headerName': '$',
        'colId':'ETC_amount',
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        'minWidth': 100,
        'maxWidth': 100,
        "aggFunc": "sum",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
    
        # "cellClass": 'ag-right-aligned-cell',
        "valueGetter":forecast_amount_vgetter,
        'valueFormatter': value_formatter
      }]
    for i, item in enumerate(pd.period_range(report_date, end_date, freq='M')):
        column_id = item.strftime('%Y-%m')
        header_month = item.strftime('%b %Y')
        forecast_children.append(
            {
                "headerName" : header_month,
                'columnGroupShow': 'open',
                "children":[
                    {
                        "field": column_id+'-cF',
                        "headerName": '%',
                        "type": [
                              "numericColumn",
                              "numberColumnFilter"
                        ],
                        'minWidth': 60,
                        'maxWidth': 60,
                        'editable':editable,
                        'suppressMenu':True,
                        'valueSetter':my_setter,
                        'valueFormatter': forecast_field_formatter
                    },
                    
                    {
                        'headerName' : '$',
                        'colId': column_id+'m$',
                        "type": [
                              "numericColumn",
                              "numberColumnFilter"
                        ],
                        "aggFunc": "sum",
                        'minWidth': 100,
                        'maxWidth': 100,
                        'suppressMenu':True,
                        'valueGetter': forecast_amount_getter,
                        'valueFormatter': amount_formatter
                    },
                    
                    
                ]
            },
        )
    return forecast_children



def configure_cost_grid_options(actual_children, forecast_children, pinned_row_data):
  gridOptions={
    "defaultColDef": {
        "minWidth":80,
        "maxWidth":120,
        "filter": True,
        "resizable": True,
        "sortable": True,
    },
    "columnDefs": [
      { 
        "headerName": "TOTAL Column",
        'field':'total_column',
        "minWidth":140,
        "maxWidth":140,
        "hide":True,
        'rowGroup':True,
      },
      { 
        "headerName": "Division",
        "field": "Division",
        "minWidth":140,
        "maxWidth":140,
        "hide":True,
        'rowGroup':True,
      },
      { "headerName": "Cost Item",
        "field": "cost_item",
        "headerTooltip":"The Cost Item code",
        'suppressMenu':True,
      },
      { 
        "field": "Cost_Item_Description",
        "headerName": "Description",
        "minWidth":150,
        "maxWidth":150,
      },
      { "headerName": "Est. At Completion",
        "field": "EAC",
        'suppressMenu':True,
        # 'editable':True,
        "cellClass": 'ag-right-aligned-cell',
        "aggFunc": "sum",
        "minWidth":135,
        "maxWidth":135,
        "valueFormatter": value_formatter
      },
      { 
        "headerName": "Forecast Method",
        "field": "forecast_method",
        "maxWidth": 125,
        'suppressMenu':True,
        "headerTooltip":"Choose a forecasting method",
        "editable": True,
        "cellEditor": 'agRichSelectCellEditor',
        "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
      },
      { 
        "headerName": "Start Date",
        'colId': "start_date",
        "editable": date_editable,
        'suppressMenu':True,
        "minWidth": 100,
        "maxWidth": 100,
        'valueGetter':date_getter,
        'valueSetter':date_setter,
      },
      { 
        "headerName": "End Date",
        'colId': "end_date",
        "editable": date_editable,
        'suppressMenu':True,
        "minWidth": 100,
        "maxWidth": 100,
        'valueGetter':date_getter,
        'valueSetter':date_setter,
      },
      { 
        "headerName": "Actual Costs To Date",
        # 'headerClass':'header-class-actual',
        # 'openByDefault':True,
        "headerTooltip":"Expand for historical monthly cost data",
        "children":actual_children
      },
      { 
        "headerName": "Est. To Completion",
        # "openByDefault":True,
        "children":forecast_children,
        # "maxWidth": 175,
      },
      
    ],
    "debug":True,
    "autoGroupColumnDef": {
        "field":"autoGroup",
        "headerName": 'Division',
        "minWidth": 175,
        "maxWidth": 175,
        "cellRendererParams": {
            "suppressCount": True,
        }
    },
    # # "rowClassRules":row_class_rules,
    # "pinnedTopRowData":pinned_row_data,
    "tooltipShowDelay":600,
    # # 'rowHeight':55,
    # 'getRowHeight': row_height,
    # 'getRowNodeId':'data.id',
    "onCellValueChanged": js_changed,
    "onCellClicked":js_clicked,
    # "onGridReady":when_grid_is_ready,
    "suppressAggFuncInHeader":True,
    # "groupIncludeFooter": True,
    # "groupIncludeTotalFooter": True,
    'animateRows':True,
    'enableCellChangeFlash':True,
    # 'enableCharts': True,
    'groupDefaultExpanded':True,
    # 'enableRangeSelection': True,
  }
  
  return gridOptions



