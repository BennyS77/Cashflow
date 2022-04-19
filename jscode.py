from st_aggrid import JsCode


forecast_field_formatter = JsCode("""
    function(params) {
        var last_date = new Date(params.column.colId.substr(0,7));
        last_date.setMonth(last_date.getMonth() - 1);
        var last_year = String(last_date.getFullYear());
        var last_month = String(last_date.getMonth()+1).padStart(2, '0');
        var last_column_string = last_year.concat("-").concat(last_month);
        var previous_cum_percentage = params.data[last_column_string.concat("-cF")];
        
         /** IF FIRST MONTH AND NO ACTIVITY --> CLEAR CELL **/
        if (isNaN(previous_cum_percentage)==true && params.value == params.data.total) {
            return '';
        }
         /** IF NO ACTIVITY FOR MONTH --> CLEAR CELL  **/
        if (params.value == previous_cum_percentage) {
            return '';
        } else {
            return parseFloat(params.value*100).toFixed(1);
        }
    }
  """)


amount_formatter = JsCode("""
    function(params) {
        if (params.value != 0) {
            return parseFloat(params.value).toLocaleString('en',{minimumFractionDigits: 0,  maximumFractionDigits: 0});
        }
    }
  """)


forecast_month_amount_getter = JsCode("""
    function(params) {
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
            if (amount == 0) {
                return ''
            } else {
                return amount * params.data.EAC
            }
        }
            /** IF FIRST FORECAST MONTH  **/  
        else {
            var amount = cum_percentage - params.data.total;
            if (amount == 0) {
                return ''
            } else {
                return amount * params.data.EAC
            }
        }
    };
""")



date_getter = JsCode("""
    function(params) {
        if (params.data.forecast_method == "Timeline") {
            if (params.column.colId == "start_date") {
                return params.data.item_start_date;
            }
            if (params.column.colId == "end_date") {
                return params.data.item_end_date;
            }
        }
        if (params.data.forecast_method == "Manual") {
            return '-';
        }
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
                console.log('start date = ', params.data.item_start_date);
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
        let item_start = new Date(params.data.item_start_date);
        let item_start_date = new Date(item_start.getFullYear(), item_start.getMonth(), item_start.getDate());
        let item_end = new Date(params.data.item_end_date);
        let item_end_date = new Date(item_end.getFullYear(), item_end.getMonth(), item_end.getDate());  
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
            var ETC = 1-params.data.total;
            return params.data.total+(duration_so_far/total_days)*ETC;
        } else {
            console.log('params.data.total = ', params.data.total);
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





