import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
from cashflow_jscode import value_formatter, js_changed, js_clicked, row_height, col_span, editable, date_editable, percent_formatter
from cashflow_jscode import forecast_percent_formatter, sparkline_data, sparkline_params, amount_formatter, cell_style_date
from cashflow_jscode import date_formatter, cell_style_percent

def configActualChildren(firstMonth, lastMonth):
    actualChildren=[{ "headerName": "Actual Costs To Date",
        "field": "ACTD",
        'columnGroupShow': 'closed',
        'suppressMenu':True,
        'maxWidth':150,
        "aggFunc": "sum",
        "cellClass": 'ag-right-aligned-cell',
        # 'headerClass':'header-class-actual',
        "valueFormatter": value_formatter
      }]
    for i in range(len(pd.period_range(firstMonth, lastMonth, freq='M'))):
        thisMonth = firstMonth + relativedelta(months=i)
        if (i % 2)==0:
            color_text = 'rgba(245,245,245,1)'
        else:
            color_text = 'rgba(250,250,250,1)'
        actualChildren.append(
            {
            "headerName" : thisMonth.strftime('%b %Y'),
            'headerClass':'header-class-actual',
            'columnGroupShow': 'open',
            "children":[
                {
                    'field': thisMonth.strftime('%b_%y')+'_%',
                    'headerName' : ' % ',
                    'maxWidth':55,
                    'suppressMenu':True,
                    # 'headerClass':'ag-right-aligned-header',
                    'headerClass':'header-class-actual',
                    # "cellClass": 'ag-right-aligned-cell',
                    # "cellClass": 'cell-class-actual',
                    "cellClassRules":cell_class_rules,
                    "valueFormatter": percent_formatter,
                    },
                {
                    'field': thisMonth.strftime('%b_%y')+'_$',
                    'headerName' : 'Amount, $',
                    'maxWidth':95,
                    'suppressMenu':True,
                    'headerClass':'header-class-actual',
                    # "cellClass": 'cell-class-actual',
                    # "cellClass": 'ag-right-aligned-cell',
                    "cellClassRules":cell_class_rules,
                    "aggFunc": "sum",
                    "valueFormatter": amount_formatter,
                    }
                ]
            },
        )
    return actualChildren


def configForecastChildren(report_date, end_date):
  forecastChildren=[{
      "headerName":"",
      "minWidth":95,
      "maxWidth":95,
      }]
  for i in range(1,len(pd.period_range(report_date, end_date, freq='M')),1):
      thisMonth = report_date + relativedelta(months=i)
      forecastChildren.append(
          {"headerName" : thisMonth.strftime(' %b %Y '),
          'columnGroupShow': 'open',
          "children":[
              { 
                'field': thisMonth.strftime('%b_%y')+'_F%',
                'headerName' : ' %',
                'maxWidth':55,
                'suppressMenu':True,
                "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
                "editable": editable,
                "cellStyle":cell_style_percent,
                "valueFormatter": forecast_percent_formatter
              },
              { 
                'field': thisMonth.strftime('%b_%y')+'_F$',
                'headerName' : ' Amount, $',
                'maxWidth':100,
                "aggFunc": "sum",
                'suppressMenu':True,
                "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
                "valueFormatter": amount_formatter
              }
            ]
          },
    )
  return forecastChildren

empty_header_area = "rgba(255,255,255,1)"
streamlit_defaut_background_color = "rgba(240,242,246,1)"  # !important"  ## F0F2F6
shade_0 = "rgba(251,252,253,1)"
shade_1 = "rgba(192,202,216,1)"
shade_1 = "rgba(179,189,209,1)"
streamlit_defaut_text_color = "rgba(49, 51, 63, 1)"
shade_0_test = "rgba(119,123,145,1)"
shade_1_test = "rgba(71,74,92,1)"
just_see_color = "rgba(230,230,230,1)"
default_color = "rgba(255,255,255,1)"
manual_background_color = "rgba(250,250,250,1)"
editable_color = "rgba(5,5,120,1)"
pinned_background_color = "rgba(240,240,240,1)"
group_row_background_color = "rgba(240,242,246,0.6)"
actual_header_background_color = "rgba(245,247,249,1)"  #"rgba(250,251,252,1)"
grid_data_font_color = "rgba(80,80,80,1)"
red_color = "rgba(240,0,0,0.8)"
yellow_color = "rgba(240,240,50,1)"

row_class_rules = {
      # "forecast-timeline": "data.forecast_method == 'Timeline'",
      # "forecast-manual": "data.forecast_method == 'Manual'",
      "pinned-row" : "node.rowPinned == 'top'",
      "group-row" : "node.group == true"
  }
cell_class_rules = {
    # "forecast-time-cellrule": "data.forecast_method == 'Timeline' && ( colDef.field == 'item_start_date' || colDef.field == 'item_end_date') ",
    # "forecast-manual-cellrule": "data.forecast_method == 'Manual' && colDef.field != 'item_start_date' && colDef.field != 'item_end_date' ",
    # "forecast-manual-cellrule2": "data.forecast_method == 'Manual' && ( colDef.field == 'item_start_date' || colDef.field == 'item_end_date') ",
    # "forecast-method": "colDef.field == 'forecast_method' ",
    # "forecast-manual-cellrule": "colDef.field != 'item_start_date'",
    # "date-cellrule": "data.forecast_method == 'Manual' && column.colId != 'item_start_date'"
    "actual-data-rows": "node.group != true && node.rowPinned != 'top'",
  }

## Custom CSS rules to be added to the component's iframe
custom_css= {
    # ".ag-header": {"font-size": "13px", 'background-color': streamlit_defaut_background_color+" !important"},  ## sets all header parameters
    # ".ag-header-cell": {'background-color':streamlit_defaut_background_color,'color':streamlit_defaut_text_color},  ## sets first header row
    # ".ag-theme-streamlit .ag-header-cell-text": {'color':'blue'},
    # ".ag-theme-streamlit .ag-header-cell-label": {'color':red_color},     ## set the font of the labels
    ".ag-header-group-cell": {'background-color': streamlit_defaut_background_color},   ## includes all header area above first header row
    # ".ag-theme-streamlit .ag-header-group-cell-label": {"flex-direction":'row-reverse'},   ## includes all header area above first header row
    # ".ag-right-aligned-cell": {"background-color":'pink'},   ## includes all header area above first header row


    # ".forecast-method": {'text-align':'center'},
    # ".forecast-timeline": {"color": grid_data_font_color},
    # ".forecast-time-cellrule": {'color': editable_color, 'text-align':'centre'},
    # ".forecast-manual-cellrule": {'color': editable_color, 'background-color': manual_background_color},
    # ".forecast-manual-cellrule2": {'color': just_see_color, 'background-color': default_color},
    ".actual-data-rows": {'background-color': actual_header_background_color},
    ".group-row": {'background-color': streamlit_defaut_background_color+" !important"},
    ".pinned-row": {"font-size":"15px",'font-style':'italic','font-weight':500,'color':streamlit_defaut_text_color+" !important"},
    ".header-class-actual":{
        'background-color': actual_header_background_color,
        "font-size":"12px",
        'font-style':'italic',
        'font-weight':400,
        'height': '100%'
        },
    ".cell-class-actual":{
        'background-color': actual_header_background_color,
        "font-size":"12px",
        'font-style':'italic',
        'text-align':'right',
        'font-weight':150,
        'height': '100%'
        },  
    ".header-class-standard":{
        'background-color': streamlit_defaut_background_color,
        "font-size":"13px",
        'font-weight':620,
        'height': '100%'
        },

    # ".header-class-streamlit":{'background-color': streamlit_defaut_background_color+"!important",'text-align':'right'},
  }


def configureGridOptions(actual_children, forecast_children, pinnedRowData):
  gridOptions={
    "defaultColDef": {
      # "minWidth": 50,
      # "maxWidth": 120,
      'headerClass':'header-class-standard',
      "filter": True,
      "resizable": True,
      "sortable": True,
    },
    "columnDefs": [
      { 
        "headerName": "Hidden Group",
        "field": "cost_group",
        'rowGroup':True,
        "hide":True,
        'suppressMenu':True,
        # 'pinned':'left',
        "maxWidth": 60,
      },
      { "headerName": "Cost Item",
        "field": "cost_item",
        "headerTooltip":"The Cost Item code",
        # 'suppressMenu':True,
        # 'pinned':'left',
        "maxWidth": 100,
        'colSpan':col_span
      },
      { "headerName": "Description",
        "field": "description",
        # 'suppressMenu':True,
        "maxWidth": 160,
      },
      { "headerName": "Estimate At Completion",
        "field": "EAC",
        'suppressMenu':True,
        "cellClass": 'ag-right-aligned-cell',
        "maxWidth": 170,
        "aggFunc": "sum",
        "valueFormatter": value_formatter
      },
      {
        "headerName":"Progress ($), %",
        "valueGetter":sparkline_data,
        "width": 200,
        "cellRenderer": 'agSparklineCellRenderer',
        "cellRendererParams": sparkline_params
      },
      { 
        "headerName": "Monthly 'Actuals'",
        "field": "Actual",
        'headerClass':'header-class-actual',
        # 'openByDefault':True,
        "headerTooltip":"Expand the Actual monthly cost data",
        "children":actual_children
      },
      
      { 
        "headerName": "Estimate To Completion",
        "field": "ETC",
        "aggFunc": "sum",
        'suppressMenu':True,
        "maxWidth": 165,
        "cellClass": 'ag-right-aligned-cell',
        "valueFormatter": value_formatter
      },
      { 
        "headerName": "Forecast Method",
        "field": "forecast_method",
        "maxWidth": 125,
        'suppressMenu':True,
        "headerTooltip":"Choose a forecasting method",
        "editable": True,
        # "cellClassRules":cell_class_rules,
        "cellEditor": 'agRichSelectCellEditor',
        "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
      },
      { 
        "headerName": "Start Date",
        "field": "item_start_date",
        "editable": date_editable,
        'suppressMenu':True,
        'valueFormatter':date_formatter,
        "maxWidth": 90,
        "type": ['dateColumn']
      },
      { 
        "headerName": "End Date",
        "field": "item_end_date",
        "editable": date_editable,
        'suppressMenu':True,
        'valueFormatter':date_formatter,
        "maxWidth": 90,
      },
      { 
        "headerName": "Forecast",
        # "openByDefault":True,
        "children":forecast_children,
        "maxWidth": 175,
      },
      
    ],
    "debug":True,
    "autoGroupColumnDef": {
        "field":"autoGroup",
        "headerName": '',
        'pinned':'left',
        "minWidth": 40,
        "cellRendererParams": {
            "suppressCount": True,
        }
    },
    "rowClassRules":row_class_rules,
    # "groupDisplayType": 'groupRows',
    "pinnedTopRowData":pinnedRowData,
    "tooltipShowDelay":400,
    # 'rowHeight':55,
    'getRowHeight': row_height,
    "onCellValueChanged": js_changed,
    "onCellClicked":js_clicked,
    "suppressAggFuncInHeader":True,
    "groupIncludeFooter": True,
    # "groupIncludeTotalFooter": True,
    'animateRows':True,
    'enableCharts': True,
    'groupDefaultExpanded':True,
    'enableRangeSelection': True,
    # 'popupParent':'document.body'

  }
  
  return gridOptions, custom_css



