import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd

def configActualChildren(firstMonth, lastMonth):
    actualChildren=[{"headerName":"","field":"Tot","minWidth":80}]
    for i in range(len(pd.period_range(firstMonth, lastMonth, freq='M'))):
        thisMonth = firstMonth + relativedelta(months=i)
        if (i % 2)==0:
            color_text = 'rgba(245,245,245,1)'
        else:
            color_text = 'rgba(250,250,250,1)'
        # st.write(thisMonth)
        actualChildren.append(
            {
            "headerName" : thisMonth.strftime('%b %Y'),
            'columnGroupShow': 'open',
            "children":[
                {
                    'field': thisMonth.strftime('%b %y')+' A%',
                    'headerName' : ' %',
                    'maxWidth':55,
                    'suppressMenu':True,
                    "valueFormatter": "parseFloat(value*100).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
                    'cellStyle':{'backgroundColor':color_text}
                    },
                {
                    'field': thisMonth.strftime('%b %y')+' A$',
                    'headerName' : ' $',
                    'maxWidth':100,
                    'suppressMenu':True,
                    "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})",
                    'cellStyle':{'backgroundColor':color_text}
                    }
                ]
            },
        )
    return actualChildren


def configForecastChildren(report_date, end_date):
  forecastChildren=[{
      "headerName":"",
    #   "field":"for",
      "minWidth":95,
      "maxWidth":95,
    #   "cellStyle": {'backgroundColor':'rgba(250,250,250,1)'}
      }]
  for i in range(1,len(pd.period_range(report_date, end_date, freq='M')),1):
      thisMonth = report_date + relativedelta(months=i)
      forecastChildren.append(
          {"headerName" : thisMonth.strftime(' %b %Y '),
          'columnGroupShow': 'open',
          "children":[
              { 'field': thisMonth.strftime('%b %y')+' F%',
                'headerName' : ' %',
                'maxWidth':55,
                'suppressMenu':True,
                # "editable": editable,
                # "cellStyle": cell_style2,
                # "valueFormatter": 'parseFloat(value).toFixed(1)+"%"'
                "valueFormatter": 'parseFloat(value).toFixed(1)'
                },
              { 'field': thisMonth.strftime('%b %y')+' F$',
                'headerName' : ' $',
                'maxWidth':100,
                'suppressMenu':True,
                # "cellStyle": {'backgroundColor':'rgba(250,250,250,1)'},
                "valueFormatter": 'parseFloat(value).toLocaleString("en",{minimumFractionDigits: 2,  maximumFractionDigits: 2})'
                }
              ]},
    )
  return forecastChildren


def configureGridOptions(actual_children, forecast_children):
  row_class_rules = {
      # "forecast-timeline": "data.forecastMethod == 'Timeline'",
      "forecast-manual": "data.forecastMethod == 'Manual'",
  }
  gridOptions={
    "defaultColDef": {
      # "minWidth": 50,
      # "maxWidth": 120,
      "filter": True,
      "resizable": True,
      "sortable": True
    },
    "columnDefs": [
      { 
        "headerName": "Group",
        "field": "costGroup",
        'suppressMenu':True,
        "maxWidth": 60,
      },
      { "headerName": "Cost Item",
        "field": "costitem",
        'suppressMenu':True,
        "maxWidth": 85,
      },
      { "headerName": "Description",
        "field": "Description",
        # 'suppressMenu':True,
        "maxWidth": 160,
      },
      { "headerName": "EAC",
        "field": "EAC",
        "type": [
          "numericColumn",
          "numberColumnFilter"
        ],
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "ACTD",
        "field": "ACTD",
        "type": [
          "numericColumn",
          "numberColumnFilter"
        ],
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "ETC",
        "field": "ETC",
        "type": [
          "numericColumn",
          "numberColumnFilter"
          ],
        "valueFormatter": "parseFloat(value).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})"
      },
      { "headerName": "Forecast Method",
        "field": "forecastmethod",
        "maxWidth": 125,
        'suppressMenu':True,
        "editable": True,
        # "cellStyle": cell_style,
        "cellEditor": 'agRichSelectCellEditor',
        "cellEditorParams": {'values': ['Timeline', 'Manual','S-curve'],},
      },
      { "headerName": "Start Date",
        "field": "startDate",
        "editable": True,
        'suppressMenu':True,
        "maxWidth": 90,
        "type": [
          "numericColumn",
          "numberColumnFilter"
          ],
      },
      { "headerName": "End Date",
        "field": "endDate",
        "editable": True,
        'suppressMenu':True,
        "maxWidth": 90,
        "type": [
          "numericColumn",
          "numberColumnFilter"
          ],
      },
      { "headerName": "Actual",
        "field": "Actual",
        "children":actual_children
      },
      { "headerName": "Forecast",
        # "openByDefault":True,
        "children":forecast_children,
        "maxWidth": 175,
      },
      
    ],
    "debug":True,
    "rowClassRules":row_class_rules,
    # "onCellValueChanged": js,
    # 'groupDefaultExpanded':True,
    # 'animateRows':True,
  }
  custom_css= {
    # ".forecast-timeline": {"color": "green !important"},
    ".forecast-manual": {"color": "red !important"},
  }
  return gridOptions, custom_css



