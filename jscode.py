from st_aggrid import JsCode

my_renderer = JsCode("""
    function(params) {
        return `<span style="margin-left: 80px">${params.value}</span>`;
    }
""")

column_combiner = JsCode("""
    function(params) {
        return params.data.cost_item.concat(" ").concat(params.data.Cost_Item_Description);
    }
""")



actual_percent_vgetter = JsCode("""
    function(params) {
        if (params.node.group != true && params.node.rowPinned != 'top') {
            return params.data.total
        }
        if (params.node.footer == true) {
            return (params.node.aggData.ACTD_amount / params.node.aggData.EAC*100)
        }
        if (params.node.leafGroup == true ) {
            return (params.node.aggData.ACTD_amount / params.node.aggData.EAC*100)
        }
        if (params.node.rowPinned == 'top') {
            return params.data.ACTD_percent
        }
        if (params.node.key === 'TOTAL:') {
            return params.node.aggData.ACTD_amount / params.node.aggData.EAC*100
        }

    };
""")


actual_percent_vformatter = JsCode("""
    function(params) {
        if (params.node.group != true && params.node.rowPinned != 'top') {
            return parseFloat(params.value).toFixed(1)
        }
        if (params.node.footer == true) {
            return parseFloat(params.value).toFixed(1)
        }
        if (params.node.leafGroup == true) {
            return parseFloat(params.value).toFixed(1)
        }
        if (params.node.rowPinned === 'top') {
            return parseFloat(params.value).toFixed(1)
        }
        if (params.node.key === 'TOTAL:') {
            return parseFloat(params.value).toFixed(1)
        }
    };
""")

actual_amount_vgetter = JsCode("""
    function(params) {
        /** NEEDS TO RETURN A NUMBER FOR THE AGGREGATION TO WORK **/
        if (params.node.group != true && params.node.rowPinned != 'top') {
            return params.data.total/100*params.data.EAC
        }
        if (params.node.rowPinned == 'top') {
            return params.data.ACTD_amount
        }

    };
""")

value_formatter = JsCode("""
    function(params) {
        if (params.node.group != true && params.node.rowPinned != 'top') {
            if (params.value > 0) {
                return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
            } else{
                return '-'
            }
        }
        if (params.node.footer == true) {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
        }
        if (params.node.leafGroup == true) {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
        }
        if (params.node.rowPinned === 'top') {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
        }
        if (params.node.key === 'TOTAL:') {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
        }
    };
  """)


forecast_amount_vgetter = JsCode("""
    function(params) {
        /** NEEDS TO RETURN A NUMBER FOR THE AGGREGATION TO WORK **/
        if (params.node.group != true && params.node.rowPinned != 'top') {
            return (100-params.data.total)/100*params.data.EAC
        }
     /*   
        if (params.node.rowPinned == 'top') {
            let EAC_total = 0;
            params.api.forEachLeafNode(calculate);  
            console.log("EAC_total:", EAC_total);
            return EAC_total;

            function calculate(node, index) {
                EAC_total = EAC_total + node.data.EAC;
                return EAC_total
            }
        }
    */
    };
""")

forecast_percent_vgetter = JsCode("""
    function(params) {
        if (params.node.group != true && params.node.rowPinned != 'top') {
            return (100-params.data.total)
        }
        if (params.node.footer == true) {
            return (params.node.aggData.ETC_amount / params.node.aggData.EAC*100)
        }
        if (params.node.leafGroup == true ) {
            return (params.node.aggData.ETC_amount / params.node.aggData.EAC*100)
        }
        if (params.node.rowPinned == 'top') {
            return params.data.ETC_percent
        }
        if (params.node.key === 'TOTAL:') {
            return params.node.aggData.ETC_amount / params.node.aggData.EAC*100
        }
    };
""")






forecast_field_formatter = JsCode("""
    function(params) {
        
        var this_month_amount_column = params.column.colId.substring(0,7).concat('m$');
        var last_date = new Date(params.column.colId.substr(0,7));
        last_date.setMonth(last_date.getMonth() - 1);
        var last_year = String(last_date.getFullYear());
        var last_month = String(last_date.getMonth()+1).padStart(2, '0');
        var last_column_string = last_year.concat("-").concat(last_month);

 /*       console.log("this_month_amount_column", this_month_amount_column);   */

        if (params.node.group != true && params.node.rowPinned != 'top') {
            var previous_cum_percentage = params.data[last_column_string.concat("-cF")];
            
            /** IF FIRST MONTH AND NO ACTIVITY --> CLEAR CELL **/
            if (isNaN(previous_cum_percentage) == true && params.value == params.data.total) {
                var to_display = parseFloat(params.value).toFixed(1);
            } else {
                /** IF NO ACTIVITY FOR MONTH --> CLEAR CELL  **/
                if (params.value == previous_cum_percentage) {
                    var to_display = '-';
                } else {
                    var to_display = parseFloat(params.value).toFixed(1);
                }
            }
            return to_display;
        }
        if (params.node.footer == true) {
            var to_display = params.node.aggData[this_month_amount_column] / params.node.aggData.EAC * 100;
            return parseFloat(to_display).toFixed(1);
        }
        if (params.node.leafGroup == true && params.node.expanded == false ) {
            var to_display = params.node.aggData[this_month_amount_column] / params.node.aggData.EAC * 100;
            return parseFloat(to_display).toFixed(1);
        }
        if (params.node.rowPinned == 'top') {
            return parseFloat(params.value).toFixed(1);
        }
        if (params.node.key === 'TOTAL:') {
            var to_display = params.node.aggData[this_month_amount_column] / params.node.aggData.EAC * 100;
            return parseFloat(to_display).toFixed(1);
        }
    }
""")


amount_formatter = JsCode("""
    function(params) {
        if (params.node.group != true) {
            if (params.value != 0) {
                return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
            } else {
                return '-'
            }
        }
        if (params.node.footer == true) {
                return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
        }
        if (params.node.leafGroup == true ) {
                return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
        }
        if (params.node.key === 'TOTAL:') {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0})
        }

    }
""")


forecast_amount_getter = JsCode("""
    function(params) {
        if (params.node.group != true && params.node.rowPinned != 'top') {
    
            var this_date = new Date(params.column.colId.substr(0,7));
            var this_year = String(this_date.getFullYear());
            var this_month = String(this_date.getMonth()+1).padStart(2, '0');
            var this_column_string = this_year.concat("-").concat(this_month);
            var cum_percentage = params.data[this_column_string.concat("-cF")];

            var last_date = new Date(params.column.colId.substr(0,7));
            last_date.setMonth(last_date.getMonth() - 1);
            var last_year = String(last_date.getFullYear());
            var last_month = String(last_date.getMonth()+1).padStart(2, '0');
            var last_column_string = last_year.concat("-").concat(last_month);
            var previous_cum_percentage = params.data[last_column_string.concat("-cF")];
    
               /**  IF NOT FIRST FORECAST MONTH **/
            if (isNaN(previous_cum_percentage)==false) {
                var amount = cum_percentage - previous_cum_percentage;
            }
                /** IF FIRST FORECAST MONTH  **/  
            else {
                var amount = cum_percentage - params.data.total;
            }
            return amount/100 * params.data.EAC
        }

        if (params.node.rowPinned == 'top') {
            var this_month_id = params.column.colId.substring(0,7);
            return params.data[this_month_id.concat('m$')]
        }
       

    };
""")



date_getter = JsCode("""
    function(params) {
        if (params.node.group != true && params.data.forecast_method == "Timeline") {
            if (params.column.colId == "start_date") {
               return params.data.item_start_date;
            }
            if (params.column.colId == "end_date") {
                return params.data.item_end_date;
            }
        }
        if (params.node.group != true && params.data.forecast_method == "Manual") {
            return '-';
        }

        function what_row_is_it(my_value) {
            return my_value;
        }
  };
  """)


my_setter = JsCode("""
    function(params) {

        console.log("woohoo:");
        this_column = params.colDef.field;
        params.data[this_column] = params.newValue;
        var trigger = 0;
        if (params.newValue == 100) {
            params.data.Cost_Item_Description = "it's finished baby!!!";
            /* params.data['2022-08-cF'] = params.newValue; */
            for (let x in params.data) {
                console.log('This column', this_column);
                console.log('x', );
                if (this_column == x) {
                    console.log('Im a legend!!!!!!!!!!!! = ', x);
                    trigger = 1;
                }
                if (trigger == 1) {
                    console.log('Feeling triggered.....');
                    params.data[x] = 100;
                }
            }
        }
        return true;
  };
""")




date_setter = JsCode("""
    function(params) {
        if (params.column.colId == "start_date") {
            params.data.item_start_date = params.newValue;
        }
        if (params.column.colId == "end_date") {
            params.data.item_end_date = params.newValue;
        }

        for (let x in params.data) {
            if (x.substr(9,1)=="F"){
                console.log('x = ', x);
                params.data[x] = calculate_cumulative_percentage(x);
            }
        }
    return true;


    function calculate_cumulative_percentage(x) {
        let this_column = x;
        let this_year = this_column.substr(0,4);
        let this_month = this_column.substr(5,2);
        let start_of_month = new Date(this_year, this_month-1, 1);
        let end_of_month = new Date(this_year, this_month, 0);

        let start_date = params.data.item_start_date.split('/');
        let item_start_date = new Date(start_date[2], start_date[1]-1, start_date[0]);
        console.log('item_start_date = ', item_start_date);
        let end_date = params.data.item_end_date.split('/');
        let item_end_date = new Date(end_date[2], end_date[1]-1, end_date[0]);
        console.log('item_end_date = ', item_end_date);

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
        if (item_end_date < start_of_month) {
            var duration_so_far = getBusinessDatesCount(item_start_date, item_end_date);
        }
        console.log('duration so far = ', duration_so_far);

        if (duration_so_far > 0) {
            var ETC = 100-params.data.total;
            return params.data.total+(duration_so_far/total_days)*ETC;
        } else {
            return params.data.total;
        }
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


percent_formatter = JsCode("""
    function(params) {
        let col_group = params.colDef.field.substr(0,7);
        let new_col = col_group.concat("-$");

        if (params.node.group != true) {
            if (params.value > 0) {
                return parseFloat(params.value).toFixed(1);
            } else {
                return '-'
            }
        }
        if (params.node.footer == true) {
            return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
        }
        if (params.node.leafGroup == true) {
            return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
        }
        if (params.node.key === 'TOTAL:') {
            return parseFloat(params.node.aggData[new_col]/params.node.aggData.EAC*100).toFixed(1);
        }
  };
  """)


value_getter = JsCode("""
    function(params) {
        var this_month_id = params.column.colId.substring(0,7);
        /** if cumulative --> let col = this_month_id.concat("-c"); **/
        let col = this_month_id;

        if (params.node.group != true && params.node.rowPinned != 'top') {
                return params.data[col]*params.data.EAC
        }
        if (params.node.rowPinned == 'top') {
            return params.data[this_month_id.concat('-$')]
        }
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
    if (params.node.group != true && params.data.forecast_method === "Timeline") {
      return 'true';
    }
  };
  """)


