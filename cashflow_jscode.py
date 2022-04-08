from st_aggrid import GridOptionsBuilder, AgGrid, JsCode


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

editable = JsCode("""
  function (params) {
    if (params.data.forecast_method === "Manual") {
      return 'true';
    }
  };
  """)

date_editable = JsCode("""
  function (params) {
    if (params.data.forecast_method === "Timeline") {
      return 'true';
    }
  };
  """)

cell_style_date = JsCode("""
  function (params) {
    if (params.node.group != true && params.data.forecast_method == "Manual") {
      return {'color':'rgba(210,210,210,1)'};
    }
    if (params.node.group != true && params.data.forecast_method == "Timeline") {
      return {'color':'rgba(60,60,60,1)'};
    }
};
""")

cell_style_percent = JsCode("""
  function (params) {
    let col_group = params.colDef.field.substr(0,8);
    let new_col = col_group.concat("$");
    if (params.node.group != true && params.data.forecast_method == "Manual") {
      return {
        'color':'rgba(60,60,60,1)',
        'border-style':'inset',
        'border-color': 'rgba(220,220,220,1)',
        'border-width': '2px'
      };
    }
    if (params.node.group != true && params.data.forecast_method == "Timeline" && params.data[new_col]>0) {
      return {
        'color':'rgba(60,60,60,1)',
        'border-style':'none',
        'background-color':'rgba(230, 95, 92, 0.1)',
/*        'background-image': 'linear-gradient(to right, rgba(255,255,255,0), rgba(255,255,255,1), rgba(255,255,255,0))'  */
      };
    }  
};
""")

cell_style_amount = JsCode("""
  function (params) {
    if (params.node.group != true  && params.node.rowPinned != 'top' && params.value>0) {
      return {
        'color':'rgba(60,60,60,1)',
/*        'border-style':'none',  */
        'background-color':'rgba(230, 95, 92, 0.1)',
      };
    }  
};
""")




js_changed = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let old_value = e.oldValue;    
    console.log('cell changed....!!!');
    console.log('node: ', e.node);
    console.log('new value: ', e.newValue);
    console.log('column: ', e.column.colId);
    if (e.column.colId == "forecast_method") {
      api.refreshCells({
        force: true,
        rowNodes: [e.node],
        });
    }
    };
""")

js_clicked = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    console.log('cell clicked....!!!!!!');
    console.log('api: ', api);
    console.log('rowIndex: ', rowIndex);
    console.log('node: ', e.node);
    console.log('id: ', e.node.id);
    console.log('key: ', e.node.key);
    console.log('new value: ', e.newValue);
    console.log('group: ', e.node.group);
    console.log('footer: ', e.node.footer);
    console.log('col_clicked: ', e.column.colId);
    };
""")

row_height = JsCode("""
  function(params) {
    if (params.node.rowPinned == 'top') {
      return 30;
    } else {
       return 30;
      }
  };
  """)

col_span = JsCode("""
  function(params) {
    if (params.node.rowPinned == 'top') {
      return 2;
    } else {
       return 1;
      }
  };
  """)

date_formatter = JsCode("""
  function(params) {
    if (params.node.group != true && params.node.rowPinned != 'top' && params.data.forecast_method == "Timeline") {
      return params.value
    }
    if (params.node.group != true && params.node.rowPinned != 'top' && params.data.forecast_method == "Manual") {
      return "-"
    }
  };
  """)


value_formatter = JsCode("""
  function(params) {
    if (params.node.group != true && params.node.rowPinned != 'top') {
      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
    }
    if (params.node.footer == true) {
      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
    }
    if (params.node.leafGroup == true && params.node.expanded == false ) {
      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
    }
    if (params.node.rowPinned === 'top') {
      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
    }
  };
  """)


percent_formatter = JsCode("""
  function(params) {
    let col_group = params.colDef.field.substr(0,7);
    let new_col = col_group.concat("$");
    if (params.node.group == true && params.node.footer == true) {
        return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
    }
    if (params.node.group != true) {
       return parseFloat(params.value*100).toFixed(1);
    }
    if (params.node.leafGroup == true && params.node.expanded == false ) {
        return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
    }
  };
  """)

amount_formatter = JsCode("""
  function(params) {
    if (params.value > 0) {
      if (params.node.group != true && params.node.rowPinned != 'top') {
        return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
      }
      if (params.node.footer == true) {
        return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
      }
      if (params.node.leafGroup == true && params.node.expanded == false ) {
        return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
      }
      if (params.node.rowPinned === 'top') {
        return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
      }
    } else {
      return ''
    }
  };
  """)




forecast_percent_formatter = JsCode("""
  function(params) {
      let col_group = params.colDef.field.substr(0,8);
      let new_col = col_group.concat("$");
      if (params.node.group == true && params.node.footer == true) {
          return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
      }
      if (params.node.group != true && params.node.rowPinned != 'top') {
        if (params.data[new_col]>0) {
          return parseFloat(params.value).toFixed(1);
        } else {
          return '' ;
        }
      }
      if (params.node.leafGroup == true && params.node.expanded == false ) {
          return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
      }
      if (params.node.rowPinned == 'top') {
        return parseFloat(params.value*100).toFixed(1);
      }

  };
  """)

sparkline_data = JsCode("""
  function(params) {
    if (params.node.group != true) {
      return [params.data.ACTD/params.data.EAC*100];
    } 
    if (params.node.group == true && params.node.footer == true) {
      return [params.node.aggData.ACTD/params.node.aggData.EAC*100];
    }
    if (params.node.leafGroup == true && params.node.expanded == false ) {
      return [params.node.aggData.ACTD/params.node.aggData.EAC*100];
    }
    if (params.node.leafGroup == true && params.node.expanded == true ) {
      return [];
    }
  }
""")


sparkline_params = JsCode("""
  function(params) {
    if (params.node.rowPinned == 'top') {
      return {
                sparklineOptions: {
                  type: 'bar',
                  fill: 'rgba(14, 52, 160,0.9)',
                  stroke: 'rgb(220,220,40,1)',
                  highlightStyle: {
                    fill: 'rgb(236, 195, 11)',
                  },
                  label: {
                    enabled: true,
                    color: 'white',
                    fontSize: 10,
                    fontWeight: 'bold',
                    formatter: function (params) {
                      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
                    },
                  },
                  paddingOuter: 0,
                  padding: {
                    top: 0,
                    bottom: 0,
                  },
                  valueAxisDomain: [0, 100],
                  axis: {
                    strokeWidth: 0,
                  },
                  tooltip: {
                    enabled: false,
                  },
                }
        };
    }

    if (params.node.group == true) {
        return {
                sparklineOptions: {
                  type: 'bar',
                  fill: 'rgba(14, 52, 160,0.8)',
                  stroke: 'rgba(20,220,220,1)',
                  highlightStyle: {
                    fill: 'rgb(236, 195, 11)',
                  },
                  label: {
                    enabled: true,
                    color: 'white',
                    fontSize: 10,
                    fontWeight: 'bold',
                    formatter: function (params) {
                      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
                    },
                  },
                  paddingOuter: 0.1,
                  padding: {
                    top: 0,
                    bottom: 0,
                  },
                  valueAxisDomain: [0, 100],
                  axis: {
                    strokeWidth: 0,
                  },
                  tooltip: {
                    enabled: false,
                  },
                }
        };
    }

    if (params.node.group != true) {
        return {
                sparklineOptions: {
                  type: 'bar',
                  fill: 'rgba(14, 52, 160,0.6)',
                  stroke: 'rgb(220,220,40,1)',
                  highlightStyle: {
                    fill: 'rgb(236, 195, 11)',
                  },
                  label: {
                    enabled: true,
                    color: 'white',
                    fontSize: 10,
                    fontWeight: 'bold',
                    formatter: function (params) {
                      return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
                    },
                  },
                  paddingOuter: 0.2,
                  padding: {
                    top: 0,
                    bottom: 0,
                  },
                  valueAxisDomain: [0, 100],
                  axis: {
                    strokeWidth: 0,
                  },
                  tooltip: {
                    enabled: false,
                  },
                }
        };
    }
  };
""")




# /***** 
#     if (col_changed === "Month_0_percent" & rowNode.data.forecastMethod === "Manual") {
#       console.log('recalculating monthly $$');
#       console.log('new percentage is: ', new_value);
#       var M0p = rowNode.data.Month_0_percent;
#       var M1p = rowNode.data.Month_1_percent;
#       var M2p = rowNode.data.Month_2_percent;
#       var Month_0_$ = (new_value-rowNode.data.actual_percent) / 100 * rowNode.data.EAC;
#       var Month_1_$ = (M1p - M0p) / 100 * rowNode.data.EAC;
#       var Month_2_$ = (M2p - M1p) / 100 * rowNode.data.EAC;
#       rowNode.setDataValue('Month_0_$', Month_0_$);
#       rowNode.setDataValue('Month_1_$', Month_1_$);
#       rowNode.setDataValue('Month_2_$', Month_2_$);
#     }

    
#     if (new_value != old_value & rowNode.data.forecastMethod === "Manual") {
#         var Month_0_$ = 777;
#         var Month_1_$ = 333;
#         console.log('column changed: ', col_changed);
#         if (col_changed != 'Month_0_$') {
#           console.log("changing value for", col_changed);
#           rowNode.setDataValue('Month_0_$', Month_0_$);
#           }
#         console.log("again???...");
#         if (col_changed != 'Month_1_$') {
#           console.log("changing value for", col_changed);
#           rowNode.setDataValue('Month_1_$', Month_1_$);
#         }

#     }
# *****/


# if (new_value === 'Manual' & col_changed === "forecastMethod") {
#       api.refreshCells({
#         force: true,
#         rowNodes: [rowNode],
#         });
#     }
#     if (new_value === 'Timeline' & col_changed === "forecastMethod") {
#       console.log('reset key for grid and reinitialize with data in dataframe');

#       api.refreshCells({
#         force: true,  
#         rowNodes: [rowNode], 
#         });
#       }


#  var Month_0_$ = rowNode.data.Month_0_percent /100 * rowNode.data.EAC;
#         rowNode.setDataValue('Month_0_$', Month_0_$);
# if (new_value === "Timeline") {
#       var f1Days = 31;
#       var f2Days = 28;
#       var numDays = rowNode.data.numDays;
#       var dollarsPerDay = rowNode.data.ETC / numDays;
#       if (numDays > f1Days) {
#           var f1Amount = f1Days * dollarsPerDay;
#           var f1Percent = f1Amount / rowNode.data.EAC * 100;
#           if ((numDays-f1Days) <= f2Days) {
#               var f2Amount = (numDays-f1Days) * dollarsPerDay;
#               var f2Percent = f2Amount / rowNode.data.EAC * 100;
#           }
#       } else {
#             var f1Amount = numDays * dollarsPerDay;
#             var f1Percent = f1Amount / rowNode.data.EAC * 100;
#             var f2Amount = 0;
#             var f2Percent = 0;
#       }
#       rowNode.setDataValue('f1Amount', f1Amount);
#       rowNode.setDataValue('f1Percent', f1Percent);
#       rowNode.setDataValue('f2Amount', f2Amount);
#       rowNode.setDataValue('f2Percent', f2Percent);
#     }
# if (col_changed === "Month_0_%") {
#         var Month_0_$ = new_value /100 * rowNode.data.EAC;
#         rowNode.setDataValue('Month_0_$', Month_0_$);

#     }



  # js = JsCode("""function(e) {
  #   let api = e.api;
  #   let rowIndex = e.rowIndex;
  #   let col_changed = e.column.colId;
  #   let new_value = e.newValue;
  #   let focused_cell = api.getFocusedCell();
  #   let rowNode2 = api.getDisplayedRowAtIndex(rowIndex);
  #   let rowNode = api.getRowNode(rowIndex);
  #   let changed_value = api.getValue(col_changed,rowNode);
  #   console.log(api,  focused_cell);
  #   console.log(rowIndex, rowNode, rowNode2, col_changed, changed_value);
  #   console.log("new value:" , new_value);
  #   if (changed_value !== 333) {
  #     let newAmount = 333;
  #     rowNode.setDataValue('forecastAmount', newAmount);
  #   }

  #   api.flashCells({
  #       rowNodes: [rowNode],
  #       columns: [col_changed],
  #       flashDelay: 350
  #       });
  #   };
  #   """)
#   /**      api.flashCells({
#         rowNodes: [rowNode],
#         columns: ['Month_0_percent'],
#         flashDelay: 350
#         });
# **/