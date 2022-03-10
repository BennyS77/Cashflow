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
    if (params.data.forecastMethod === "Manual") {
      return 'true';
    }
  };
  """)


cellEditorSelector = JsCode("""
  function (params) {
    if (params.data.forecastMethod === "Manual") {
      return {
        component: 'agRichSelectCellEditor',
        params: {
          values: [30, 40],
        },
      };
    }
    if (params.data.forecastMethod === "Timeline") {
      return {
        component: 'ttt',
        params: {
          values: [30, 40],
        },
      };
    }
  }
  """)



cell_style = JsCode("""
  function (params) {
    if (params.data.forecastMethod == "Manual") {
      return {'color':'black','backgroundColor':'rgba(250,250,250,1)'};
    } else {
      return {'color':'black','backgroundColor':'white'};
      }
};
""")

cell_style2 = JsCode("""
  function (params) {
    if (params.data.forecastMethod == "Timeline") {
      return {'color':'black','backgroundColor':'rgba(250,250,250,1)'};
    } else {
      return {'color':'black','backgroundColor':'white'};
      }
};
""")


js = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let col_changed = e.column.colId;
    let new_value = e.newValue;
    let old_value = e.oldValue;
    let rowNode = api.getRowNode(rowIndex);
    console.log('onCellValueChanged fired!!!');
    console.log(rowIndex, rowNode);
    console.log('api: ', api);
    if (new_value === 'Manual' & col_changed === "forecastMethod") {
      api.refreshCells({
        force: true,
        rowNodes: [rowNode],
        });
    }
    if (new_value === 'Timeline' & col_changed === "forecastMethod") {
      console.log('reset key for grid and reinitialize with data in dataframe');

      api.refreshCells({
        force: true,  
        rowNodes: [rowNode], 
        });
      }
    };
""")



vg_ETC = JsCode("""
  function(params) {
    return parseFloat(params.data.EAC-params.data.ACTD).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2});
  };
  """)

vg_forecastAmount = JsCode(""" function(params) {
  let ETC = params.data.EAC - params.data.ACTD;
  if (params.data.forecastMethod === 'Timeline') {
      return ETC/3
  } else {
      return 0
    }
};""")

vg_forecastPercent = JsCode(""" function(params) {
  let ETC = params.data.EAC - params.data.ACTD;
  let amountSoFar = ETC/3;
  if (params.data.forecastMethod === 'Timeline') {
      return amountSoFar/params.data.EAC
  } else {
      return 0
    }
};""")


showDaysFormatter  = JsCode(""" function(params) {
  if (params.data.forecastMethod == 'Timeline') {
      return params.data.numDaysDuration
  } else {
      return '-'
    }
};""")



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