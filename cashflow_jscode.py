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

js = JsCode("""function(e) {
    let api = e.api;
    let rowIndex = e.rowIndex;
    let col_changed = e.column.colId;
    let new_value = e.newValue;
    let rowNode = api.getRowNode(rowIndex);

    console.log(rowIndex, rowNode);
    console.log("new value:" , new_value);

    if (new_value === "Timeline") {
      var f1Days = 31;
      var f2Days = 28;
      var numDays = rowNode.data.numDays;
      var dollarsPerDay = rowNode.data.ETC / numDays;
      if (numDays > f1Days) {
          var f1Amount = f1Days * dollarsPerDay;
          var f1Percent = f1Amount / rowNode.data.EAC * 100;
          if ((numDays-f1Days) <= f2Days) {
              var f2Amount = (numDays-f1Days) * dollarsPerDay;
              var f2Percent = f2Amount / rowNode.data.EAC * 100;
          }
      } else {
            var f1Amount = numDays * dollarsPerDay;
            var f1Percent = f1Amount / rowNode.data.EAC * 100;
            var f2Amount = 0;
            var f2Percent = 0;
      }
      rowNode.setDataValue('f1Amount', f1Amount);
      rowNode.setDataValue('f1Percent', f1Percent);
      rowNode.setDataValue('f2Amount', f2Amount);
      rowNode.setDataValue('f2Percent', f2Percent);

    }
    };
    """)
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
