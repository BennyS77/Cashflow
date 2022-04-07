import streamlit as st
from dateutil.relativedelta import relativedelta
import pandas as pd
from cashflow_jscode import value_formatter, js_changed, js_clicked, row_height, col_span, editable, date_editable, percent_formatter
from cashflow_jscode import forecast_percent_formatter, sparkline_data, sparkline_params, amount_formatter, cell_style_date
from cashflow_jscode import date_formatter, cell_style_percent, cell_style_amount




def configure_summary_grid_options():
  gridOptions={
    "defaultColDef": {
      "minWidth": 150,
      # 'width': 'flex',
      "filter": True,
      "resizable": True,
      "sortable": True,
    },
    "columnDefs": [
       { "headerName": "Month",
        "field": "0",
        # "minWidth": 100,
      },
      { "headerName": "Cost, $",
        "field": "cost",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
        "valueFormatter":"parseFloat(value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
        # "maxWidth": 160,
      },
      { "headerName": "Revenue, $",
        "field": "revenue",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
        "valueFormatter":"parseFloat(value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
        # 'suppressMenu':True,
        # "maxWidth": 170,
      },
      {
        "headerName":"Monthly Cashflow, $",
        "field": "cashflow",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
        "valueFormatter":"parseFloat(value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
        # "valueGetter":"parseFloat(data.revenue - data.cost).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
      },
      {
        "headerName":"Cumulative Cashflow, $",
        "field": "cum_cashflow",
        "type": [
                      "numericColumn",
                      "numberColumnFilter"
                    ],
        "valueFormatter":"parseFloat(value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})"
        # "maxWidth": 200,
      },  
    ],
    "debug":True,
  }
  
  return gridOptions



