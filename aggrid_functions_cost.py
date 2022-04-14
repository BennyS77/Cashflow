import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
from cashflow_jscode import value_formatter, js_changed, js_clicked, row_height, col_span, editable, date_editable, percent_formatter
from cashflow_jscode import another_formatter, actual_cum_perc_getter, sparkline_data, sparkline_params, amount_formatter, cell_style_date
from cashflow_jscode import date_formatter, simple_forecast_amount_getter, forecast_cum_perc_getter, simple_getter, simple_setter, cell_style_percent, value_getter, cell_style_amount, forecast_amount_getter, forecast_percentage_getter

def config_actual_cost_children(firstMonth, lastMonth):
    actual_children=[{ "headerName": "Actual Costs To Date",
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        "aggFunc": "sum",
        "cellClass": 'ag-right-aligned-cell',
        "valueGetter":"parseFloat(data.total * data.EAC).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
      }]
    for i, item in enumerate(pd.period_range(firstMonth, lastMonth, freq='M')):
        column_id = item.strftime('%Y-%m')
        header_month = item.strftime('%b %Y')
        children_header = (firstMonth + relativedelta(months=i)).strftime('%b_%y')+'_'
        actual_children.append(
            {
                "headerName" : header_month,
                'columnGroupShow': 'open',
                "children":[
                    {
                        'field': column_id+'-c',
                        # 'headerName' : ' % ',
                        'minWidth': 70,
                        'maxWidth': 80,
                        'suppressMenu':True,
                        "valueFormatter": percent_formatter,
                    },
                    # {
                    #     'colId': item.strftime('%Y-%m-1'),
                    #     'headerName' : item.strftime('%Y-%m-1'),
                    #     'minWidth': 90,
                    #     'maxWidth': 90,
                    #     'suppressMenu':True,
                    #     "valueGetter": actual_cum_perc_getter
                    # },
                    {
                        'headerName' : ' $ ',
                        'colId': column_id+'-$',
                        'minWidth': 70,
                        'maxWidth': 90,
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
                        # 'headerName' : 'c%',
                        'minWidth': 90,
                        'maxWidth': 90,
                        'editable':editable,
                        'suppressMenu':True,
                        'valueFormatter':another_formatter
                    },
                    # {
                    #     'headerName' :  column_id,
                    #     'colId': column_id,
                    #     'minWidth': 90,
                    #     'maxWidth': 90,
                    #     'editable':editable,
                    #     'suppressMenu':True,
                    #     'valueGetter':another_formatter
                    # },
                    {
                        'headerName' : column_id+'%',
                        'colId': column_id+'%',
                        'minWidth': 100,
                        'maxWidth': 110,
                        'editable':True,
                        'suppressMenu':True,
                        "valueGetter": forecast_cum_perc_getter
                        # "valueGetter": simple_getter,
                        # "valueSetter": simple_setter
                    },
                    {
                        'headerName' : '$',
                        'colId': column_id+'$',
                        'minWidth': 70,
                        'maxWidth': 90,
                        'suppressMenu':True,
                        "valueGetter": simple_forecast_amount_getter
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
      { "headerName": "Estimate At Completion",
        "field": "EAC",
        'suppressMenu':True,
        "cellClass": 'ag-right-aligned-cell',
        "aggFunc": "sum",
        "valueFormatter": value_formatter
      },
      { 
        "headerName": "Monthly 'Actuals'",
        "field": "Actual",
        'headerClass':'header-class-actual',
        # 'openByDefault':True,
        "headerTooltip":"Expand for historical monthly cost data",
        "children":actual_children
      },
      { 
        "headerName": "Estimate To Completion",
        "aggFunc": "sum",
        'suppressMenu':True,
        "maxWidth": 165,
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
      { 
        "headerName": "Start Date",
        "field": "item_start_date",
        "editable": date_editable,
        'suppressMenu':True,
        'valueFormatter':date_formatter,
        "minWidth": 100,
        "maxWidth": 100,
        "type": ['dateColumn']
      },
      { 
        "headerName": "End Date",
        "field": "item_end_date",
        "editable": date_editable,
        'suppressMenu':True,
        'valueFormatter':date_formatter,
        "minWidth": 100,
        "maxWidth": 100,
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
    "onCellValueChanged": js_changed,
    "onCellClicked":js_clicked,
    "suppressAggFuncInHeader":True,
    # "groupIncludeFooter": True,
    # # "groupIncludeTotalFooter": True,
    # 'animateRows':True,
    # 'enableCharts': True,
    'groupDefaultExpanded':True,
    # 'enableRangeSelection': True,
  }
  
  return gridOptions



