import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
from cashflow_jscode import value_formatter, js_changed, js_clicked, row_height, col_span, editable, date_editable, percent_formatter
from cashflow_jscode import date_formatter, value_getter, cell_style_amount
from jscode import date_getter, date_setter, forecast_month_amount_getter, forecast_field_formatter, amount_formatter

def config_actual_cost_children(firstMonth, lastMonth):
    actual_children=[{ "headerName": "Costs To Date",
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        'minWidth': 110,
        'maxWidth': 110,
        "aggFunc": "sum",
        "cellClass": 'ag-right-aligned-cell',
        "valueGetter":"parseFloat(data.total * data.EAC).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
      }]
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
                        'minWidth': 60,
                        'maxWidth': 60,
                        'suppressMenu':True,
                        "valueFormatter": percent_formatter,
                    },
                    {
                        'headerName' : ' $ ',
                        'colId': column_id+'-$',
                        'minWidth': 70,
                        'maxWidth': 70,
                        'suppressMenu':True,
                        "valueGetter": value_getter
                    },
                ]
            },
        )
    return actual_children


def config_forecast_cost_children(report_date, end_date):
    forecast_children=[{
        "headerName":"",
        "minWidth":95,
        "maxWidth":95,
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
                        'minWidth': 60,
                        'maxWidth': 60,
                        'editable':editable,
                        'suppressMenu':True,
                        'valueFormatter': forecast_field_formatter
                    },
                    {
                        'headerName' : '$',
                        'colId': column_id+'m%',
                        'minWidth': 100,
                        'maxWidth': 100,
                        'suppressMenu':True,
                        'valueGetter': forecast_month_amount_getter,
                        'valueFormatter': amount_formatter
                    },
                    
                    
                ]
            },
        )
    return forecast_children



def configure_cost_grid_options(actual_children, forecast_children):
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
        "headerName": "Division",
        "field": "Division",
        # "hide":True,
        # 'rowGroup':True,
      },
      { "headerName": "Cost Item",
        "field": "cost_item",
        "headerTooltip":"The Cost Item code",
        'suppressMenu':True,
      },
      { "headerName": "Description",
        "field": "Cost_Item_Description",
      },
      { "headerName": "Est. At Completion",
        "field": "EAC",
        'suppressMenu':True,
        "cellClass": 'ag-right-aligned-cell',
        "aggFunc": "sum",
        "minWidth":135,
        "maxWidth":135,
        "valueFormatter": value_formatter
      },
      { 
        "headerName": "Historical",
        "field": "Actual",
        'headerClass':'header-class-actual',
        # 'openByDefault':True,
        "headerTooltip":"Expand for historical monthly cost data",
        "children":actual_children
      },
      { 
        "headerName": "Est. To Completion",
        "aggFunc": "sum",
        'suppressMenu':True,
        "minWidth": 135,
        "maxWidth": 135,
        "cellClass": 'ag-right-aligned-cell',
        "valueGetter":"parseFloat(data.EAC-(data.total * data.EAC)).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
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
      # { 
      #   "headerName": "Start Date",
      #   "field": "item_start_date",
      #   "editable": date_editable,
      #   'suppressMenu':True,
      #   'valueFormatter':date_formatter,
      #   "minWidth": 100,
      #   "maxWidth": 100,
      #   "type": ['dateColumn']
      # },
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
      # { 
      #   "headerName": "End Date",
      #   "field": "item_end_date",
      #   "editable": date_editable,
      #   'suppressMenu':True,
      #   'valueFormatter':date_formatter,
      #   "minWidth": 100,
      #   "maxWidth": 100,
      # },
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
        "headerName": "Forecast",
        "openByDefault":True,
        "children":forecast_children,
        "maxWidth": 175,
      },
      
    ],
    "debug":True,
    "autoGroupColumnDef": {
        "field":"autoGroup",
        "headerName": 'Division',
        "cellRendererParams": {
            "suppressCount": True,
        }
    },
    # # "rowClassRules":row_class_rules,
    # "pinnedTopRowData":pinnedRowData,
    # "tooltipShowDelay":600,
    # # 'rowHeight':55,
    # 'getRowHeight': row_height,
    # "onCellValueChanged": js_changed,
    # "onCellClicked":js_clicked,
    # "onGridReady":when_grid_is_ready,
    "suppressAggFuncInHeader":True,
    # "groupIncludeFooter": True,
    # # "groupIncludeTotalFooter": True,
    # 'animateRows':True,
    # 'enableCharts': True,
    'groupDefaultExpanded':True,
    # 'enableRangeSelection': True,
  }
  
  return gridOptions



