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
    let focused_cell = api.getFocusedCell();
    let rowNode = api.getDisplayedRowAtIndex(rowIndex);
    let changed_value = api.getValue(col_changed,rowNode);
    console.log(api,  focused_cell);
    console.log(rowIndex, col_changed, changed_value);
    api.flashCells({
        rowNodes: [rowNode],
        columns: [col_changed],
        flashDelay: 250
        });
    };
    """)
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
