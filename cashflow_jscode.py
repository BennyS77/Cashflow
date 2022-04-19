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

    let rowNode = api.getRowNode(rowIndex);
    
    if (e.column.colId == "item_start_date") {
      rowNode.setDataValue("EAC", 77);
    }
    };
""")

js_clicked = JsCode("""function(e) {
    console.log('cell clicked....!!!!!!');

    console.log('column: ', e.column);
    console.log('colDef: ', e.colDef);
    console.log('value: ', e.value);
    console.log('node: ', e.node);
    console.log('data: ', e.data);
    console.log('rowIndex: ', e.rowIndex);
    console.log('context: ', e.context);
    console.log('event: ', e);
    console.log('GridAPI: ', e.api);
    console.log('columnAPI: ', e.columnApi);

    console.log('id: ', e.node.id);
    console.log('group: ', e.node.group);
    console.log('col_id: ', e.column.colId);
    console.log('col_field: ', e.colDef.field);
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
    if (params.value > 0) {
      if (params.node.group == true && params.node.footer == true) {
          return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
      }
      if (params.node.group != true) {
        return parseFloat(params.value*100).toFixed(1);
      }
      if (params.node.leafGroup == true && params.node.expanded == false ) {
          return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
      }
    } else {
      return ''
    }
  };
  """)

## Calculate actual cumulative percentages
actual_cum_perc_getter = JsCode("""
  function(params) {
    var this_date = new Date(params.column.colId);
    var this_year = String(this_date.getFullYear());
    var this_month = String(this_date.getMonth()+1).padStart(2, '0');
    var this_column_string = this_year.concat("-").concat(this_month).concat("-1");

    var last_date = new Date(params.column.colId);
    last_date.setMonth(last_date.getMonth() - 1);
    var last_year = String(last_date.getFullYear());
    var last_month = String(last_date.getMonth()+1).padStart(2, '0');
    var last_column_string = last_year.concat("-").concat(last_month).concat("-1");

    var this_month_percent = params.data[this_year.concat("-").concat(this_month)];
    var last_month_total = params.data[last_column_string];

    console.log("Start: ");
    console.log("this_date = ", this_date);
    console.log("this_column_string = ", this_column_string);
    console.log("last_column_string = ", last_column_string);
    console.log("last_month_total = ", last_month_total);


    if (last_month_total > 0) {
      var value = this_month_percent + last_month_total;
    } else {
      var value = this_month_percent;
    }
    if (value > 0) {
      return parseFloat(value*100).toFixed(1);
      } else {
        return ''
      }

};
""")



value_getter = JsCode("""
  function(params) {
      var this_month_id = params.column.colId.substring(0,7);
      let col = this_month_id.concat("-c");
      if (params.data[col] > 0) {
        return parseFloat(params.data[col]*params.data.EAC).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
      } else {
        return ''
      }
  };
  """)


## Calculate monthly forecast amounts ##
forecast_amount_getter = JsCode("""
  function(params) {
    var this_column = params.column.colId;
    var this_year = params.column.colId.substr(0,4);
    var this_month = params.column.colId.substr(5,2);
    var start_of_month = new Date(this_year, this_month-1, 1);
    var end_of_month = new Date(this_year, this_month, 0);
    var item_start = new Date(params.data.item_start_date);
    var item_start_date = new Date(item_start.getFullYear(), item_start.getMonth(), item_start.getDate());
    var item_end = new Date(params.data.item_end_date);
    var item_end_date = new Date(item_end.getFullYear(), item_end.getMonth(), item_end.getDate());  

/*    console.log("this_column = ", this_column);
    console.log("this_year = ", this_year);
    console.log("this_month = ", this_month);
    console.log("start_of_month = ", start_of_month);
    console.log("end_of_month = ", end_of_month);
    console.log("item_start_date = ", item_start_date);
    console.log("item_end_date = ", item_end_date);
*/

    let total_days = getBusinessDatesCount(item_start_date, item_end_date);   

    if (item_start_date < start_of_month && item_end_date > end_of_month) {
      var num_of_days = getBusinessDatesCount(start_of_month, end_of_month);
    }

    if (item_start_date >= start_of_month && item_start_date <= end_of_month && item_end_date > end_of_month) {
      var num_of_days = getBusinessDatesCount(item_start_date, end_of_month);
    }

    if (item_start_date >= start_of_month && item_end_date <= end_of_month) {
      var num_of_days = getBusinessDatesCount(item_start_date, item_end_date);
    }

    if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
      var num_of_days = getBusinessDatesCount(start_of_month, item_end_date);
    }
    if (item_start_date > end_of_month || item_end_date < start_of_month) {
      var num_of_days = 0
    }  

    if (num_of_days > 0 ) {
      var ETC_amount = (1-params.data.total)*params.data.EAC;
      return parseFloat(num_of_days/total_days*ETC_amount).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
    } else {
      return ''
    }

    function getBusinessDatesCount(startDate, endDate) {
        let count = 0;
        const curDate = new Date(startDate.getTime());
        while (curDate <= endDate) {
            const dayOfWeek = curDate.getDay();
            if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
            curDate.setDate(curDate.getDate() + 1);
        }
        return count;
    }

  };
  """)

## Calculate the cumulative forecast percentages.
forecast_cum_perc_getter = JsCode("""
  function(params) {
   if (params.data.forecast_method == "Timeline") {
    var this_column = params.column.colId;
    var this_year = params.column.colId.substr(0,4);
    var this_month = params.column.colId.substr(5,2);
    var start_of_month = new Date(this_year, this_month-1, 1);
    var end_of_month = new Date(this_year, this_month, 0);

    
    var item_start = new Date(params.data.item_start_date);
    console.log(item_start);
    var item_start_date = new Date(item_start.getFullYear(), item_start.getMonth(), item_start.getDate());
    var item_end = new Date(params.data.item_end_date);
    var item_end_date = new Date(item_end.getFullYear(), item_end.getMonth(), item_end.getDate());  

    let total_days = getBusinessDatesCount(item_start_date, item_end_date);   

    if (item_start_date > end_of_month) {
      var duration_so_far = 0;
    }

    if (item_start_date >= start_of_month && item_start_date <= end_of_month && item_end_date > end_of_month) {
      var duration_so_far = getBusinessDatesCount(item_start_date, end_of_month);
    }

    if (item_start_date < start_of_month && item_end_date > end_of_month) {
      var duration_so_far = getBusinessDatesCount(item_start_date, end_of_month);
    }

    if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
      var duration_so_far = getBusinessDatesCount(item_start_date, item_end_date);
    }

    if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
      var duration_so_far = getBusinessDatesCount(item_start_date, item_end_date);
    }

    if (duration_so_far > 0) {
      var ETC = 1-params.data.total;
      return parseFloat((params.data.total+(duration_so_far/total_days)*ETC)*100).toFixed(1);
    } else {
      return parseFloat(params.data.total*100).toFixed(1)
    }

  } else if (params.data.forecast_method == "Manual") {
    var column_string = params.column.colId.substring(0,7).concat("-cF");
    return parseFloat(params.data[column_string]).toFixed(1);
  }

    function getBusinessDatesCount(startDate, endDate) {
        let count = 0;
        const curDate = new Date(startDate.getTime());
        while (curDate <= endDate) {
            const dayOfWeek = curDate.getDay();
            if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
            curDate.setDate(curDate.getDate() + 1);
        }
        return count;
    }
   
};
""")


## Calculate the monthly forecast percentages (ie not cumulative)
forecast_percentage_getter= JsCode("""
function(params) {
  if (params.data.forecast_method == "Timeline") {
    var this_column = params.column.colId;
    var this_year = params.column.colId.substr(0,4);
    var this_month = params.column.colId.substr(5,2);
    var start_of_month = new Date(this_year, this_month-1, 1);
    var end_of_month = new Date(this_year, this_month, 0);
    var item_start = new Date(params.data.item_start_date);
    var item_start_date = new Date(item_start.getFullYear(), item_start.getMonth(), item_start.getDate());
    var item_end = new Date(params.data.item_end_date);
    var item_end_date = new Date(item_end.getFullYear(), item_end.getMonth(), item_end.getDate());  

    let total_days = getBusinessDatesCount(item_start_date, item_end_date);   

         /** item starts before month and ends after month **/
    if (item_start_date < start_of_month && item_end_date > end_of_month) {
      var num_of_days = getBusinessDatesCount(start_of_month, end_of_month);
    }

        /** item starts in month and ends after month  **/
    if (item_start_date >= start_of_month && item_start_date <= end_of_month && item_end_date > end_of_month) {
      var num_of_days = getBusinessDatesCount(item_start_date, end_of_month);
    }

        /** item starts and finishes in same month **/
    if (item_start_date >= start_of_month && item_end_date <= end_of_month) {
      var num_of_days = getBusinessDatesCount(item_start_date, item_end_date);
    }

        /** item starts before month and ends in month  **/
    if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
      var num_of_days = getBusinessDatesCount(start_of_month, item_end_date);
    }
        /** either item hasnt started yet or has already ended. **/
    if (item_start_date > end_of_month || item_end_date < start_of_month) {
      var num_of_days = 0
    }
      return parseFloat((num_of_days/total_days)*(1-params.data.total)*params.data.EAC).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
  
  } else if (params.data.forecast_method == "Manual"){
      var this_column = params.column.colId;
    return this_column
  }

    function getBusinessDatesCount(startDate, endDate) {
        let count = 0;
        const curDate = new Date(startDate.getTime());
        while (curDate <= endDate) {
            const dayOfWeek = curDate.getDay();
            if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
            curDate.setDate(curDate.getDate() + 1);
        }
        return count;
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


simple_getter = JsCode("""
  function(params) {

    var this_date = new Date(params.column.colId);
    var this_year = String(this_date.getFullYear());
    var this_month = String(this_date.getMonth()+1).padStart(2, '0');
    var this_column_string = this_year.concat("-").concat(this_month);
    var cum_percentage = params.data[this_column_string.concat("-cF")];

    var last_date = new Date(params.column.colId);
    last_date.setMonth(last_date.getMonth() - 1);
    var last_year = String(last_date.getFullYear());
    var last_month = String(last_date.getMonth()+1).padStart(2, '0');
    var last_column_string = last_year.concat("-").concat(last_month);
    var previous_cum_percentage = params.data[last_column_string.concat("-cF")];

    if (isNaN(previous_cum_percentage)==false) {
      return parseFloat((cum_percentage - previous_cum_percentage)*100).toFixed(1);
      } else {
        return parseFloat((cum_percentage-params.data.total)*100).toFixed(1);
      }

  };
  """)

another_formatter = JsCode("""
  function(params) {
    if (params.data.forecast_method == "Timeline") {
      var this_column = params.column.colId;
      var this_year = params.column.colId.substr(0,4);
      var this_month = params.column.colId.substr(5,2);
      var start_of_month = new Date(this_year, this_month-1, 1);
      var end_of_month = new Date(this_year, this_month, 0);
      var item_start = new Date(params.data.item_start_date);
      var item_start_date = new Date(item_start.getFullYear(), item_start.getMonth(), item_start.getDate());
      var item_end = new Date(params.data.item_end_date);
      var item_end_date = new Date(item_end.getFullYear(), item_end.getMonth(), item_end.getDate());  

      let total_days = getBusinessDatesCount(item_start_date, item_end_date);   

      if (item_start_date > end_of_month) {
        var duration_so_far = 0;
      }

      if (item_start_date >= start_of_month && item_start_date <= end_of_month && item_end_date > end_of_month) {
        var duration_so_far = getBusinessDatesCount(item_start_date, end_of_month);
      }

      if (item_start_date < start_of_month && item_end_date > end_of_month) {
        var duration_so_far = getBusinessDatesCount(item_start_date, end_of_month);
      }

      if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
        var duration_so_far = getBusinessDatesCount(item_start_date, item_end_date);
      }

      if (item_start_date < start_of_month && item_end_date >= start_of_month && item_end_date <= end_of_month) {
        var duration_so_far = getBusinessDatesCount(item_start_date, item_end_date);
      }

      if (duration_so_far > 0) {
        var ETC = 1-params.data.total;
        return parseFloat((params.data.total+(duration_so_far/total_days)*ETC)*100).toFixed(1);
      } else {
        return parseFloat(params.data.total*100).toFixed(1);
      }
    } else if (params.data.forecast_method == "Manual"){
      return parseFloat(params.value).toFixed(3);
    
    }

    function getBusinessDatesCount(startDate, endDate) {
        let count = 0;
        const curDate = new Date(startDate.getTime());
        while (curDate <= endDate) {
            const dayOfWeek = curDate.getDay();
            if(dayOfWeek !== 0 && dayOfWeek !== 6) count++;
            curDate.setDate(curDate.getDate() + 1);
        }
        return count;
    }
    
   
  };
  """)




simple_forecast_amount_getter = JsCode("""
  function(params) {
    var this_date = new Date(params.column.colId);
    var this_year = String(this_date.getFullYear());
    var this_month = String(this_date.getMonth()+1).padStart(2, '0');
    var this_column_string = this_year.concat("-").concat(this_month);
    var cum_percentage = params.data[this_column_string.concat("-cF")];

    var last_date = new Date(params.column.colId);
    last_date.setMonth(last_date.getMonth() - 1);
    var last_year = String(last_date.getFullYear());
    var last_month = String(last_date.getMonth()+1).padStart(2, '0');
    var last_column_string = last_year.concat("-").concat(last_month);
    var previous_cum_percentage = params.data[last_column_string.concat("-cF")];

  /**  IF NOT FIRST FORECAST MONTH **/
    if (isNaN(previous_cum_percentage)==false) {
      var amount = (previous_cum_percentage)*100;
      return parseFloat(amount).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
    }
  /** IF FIRST FORECAST MONTH  **/  
    else {
      var amount = (cum_percentage - params.data.total )*100;
      return parseFloat(amount).toLocaleString('en',{minimumFractionDigits: 2,  maximumFractionDigits: 2})
      }
  };
  """)

simple_setter = JsCode("""
  function(params) {
    if (params.data.forecast_method == "Manual") {
      var cum_percentage = params.newValue;
      var cum_amount = cum_percentage * params.data.EAC;
      params.data["2022-04-cF"] = params.newValue;
      return true;
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