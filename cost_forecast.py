import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
from st_aggrid import AgGrid
from dateutil.relativedelta import relativedelta
from visuals import gantt_chart, bar_chart
from my_config import page_config_and_session_state
from cost_data import  calculate_cost_data_for_the_grid,get_cost_data_and_date_range, get_eac_data
from cost_data import user_input_variables, page_layout
from aggrid_functions import configActualChildren, configForecastChildren, configureGridOptions
from aggrid_functions_revenue import configure_revenue_grid_options, config_revenue_forecast_children, config_revenue_actual_children
from aggrid_functions_summary import configure_summary_grid_options
from database_operations import writeDetailsToDatabase, readDetailsFromDatabase, drop_table, update_table



# page_config_and_session_state()

testing = False

if testing == False:

    if st.session_state.new_session == True:
        page_layout()

    user_input_variables()

    # st.write(st.session_state.cost_click)
    # st.write(st.session_state.revenue_click)
    # st.write(st.session_state.summary_click)

    try:
        st.session_state.forecast_data_table_name = ('forecast_data_'+st.session_state.company+st.session_state.job).lower()
    except:
        test = 4

    if st.session_state.forecast_table_exists == True:
        # st.sidebar.write("""   Forecast table is in database:  """ )
        all_forecast_data = readDetailsFromDatabase()
        if st.session_state.reporting_month_data_exists == True:
            # st.sidebar.write("""   Reporting Month data is in database:  """ )
            month_data = all_forecast_data.loc[all_forecast_data['reporting_month'] == st.session_state.reporting_month]



    if st.session_state.reporting_month_data_exists == False:
        """   Reporting Month data is NOT in database.  """   
        
    if st.session_state.forecast_table_exists == False:
        """     Forecast table is NOT in database.
                It should never not be by here though,
                because it should of been created.
        """ 


if testing == True:
    st.session_state.creds = {"username":'317016'+'\\'+'BenStewart', "password":'Woerifjoi439856'}
    st.session_state.company = 'G01'
    st.session_state.job = 'PD140479'
    st.session_state.forecast_data_table_name = ('forecast_data_'+st.session_state.company+st.session_state.job).lower()
    st.session_state.reporting_month = datetime(2022, 2, 28)
    if st.session_state.new_session == True:
        st.session_state.all_forecast_data = readDetailsFromDatabase()
        st.session_state.reporting_month_forecast_data = st.session_state.all_forecast_data.loc[st.session_state.all_forecast_data['reporting_month'] == st.session_state.reporting_month]
        # st.write("reporting_month_forecast_data from database...")
    # else:
        # st.write("reporting_month_forecast_data from session state...")
    # st.write(st.session_state.reporting_month_forecast_data.head(5))
    st.session_state.forecast_end_date =  st.session_state.reporting_month_forecast_data['forecast_end_date'].iloc[0]
    st.session_state.ready_for_grid = True




if st.session_state.ready_for_grid:

    st.sidebar.markdown("# ")
    st.sidebar.markdown("# ")

    include_completed_item = st.sidebar.checkbox("Include completed items in table:", value=True)
    grid_height = st.sidebar.slider("Table height:", min_value=300, max_value=1200, value=600, step=20, key='grid_height')

    cost_data, date_range = get_cost_data_and_date_range()
    grid_cost_data, pinned_row_data = calculate_cost_data_for_the_grid(cost_data, st.session_state.reporting_month_forecast_data, date_range)
    actual_children = configActualChildren(date_range[0], st.session_state.reporting_month)
    forecast_children = configForecastChildren(st.session_state.reporting_month, st.session_state.forecast_end_date)
    gridOptions, custom_css = configureGridOptions(actual_children, forecast_children, pinned_row_data)
    grid_cost_data['item_start_date']=grid_cost_data['item_start_date'].apply(lambda x: x.strftime("%d/%m/%Y"))
    grid_cost_data['item_end_date']=grid_cost_data['item_end_date'].apply(lambda x: x.strftime("%d/%m/%Y"))
    grid_cost_data.drop('current_month', inplace=True, axis=1)

    
    graph_dict = pinned_row_data[0]
    def search(my_dict, search_string):
        key_list = []
        value_list = []
        for key, value in my_dict.items():
            if search_string in key:
                key_list.append(key[:6])
                value_list.append(value)
        return key_list, value_list

    all_months, all_cost_amounts = search(graph_dict, '$')
    number_of_months = len(all_months)
    actual_months, actual_cost_amounts = search(graph_dict, '_$')
    number_of_actual_months = len(actual_months)
    forecast_months, forecast_cost_amounts = search(graph_dict, 'F$')
    number_of_forecast_months = len(forecast_months)
    # all_months, cost_amounts = search(graph_dict, 'F$')

    if len(st.session_state.revenue_amounts)==0:
            st.session_state.revenue_amounts = [item *  (0.8 + (random.random()*0.7)) for item in all_cost_amounts]

    cashflow =[int(item1 - item2) for (item1, item2) in zip(st.session_state.revenue_amounts,all_cost_amounts)]
    fig = bar_chart(all_months, all_cost_amounts, st.session_state.revenue_amounts, cashflow, number_of_actual_months)
    


    ## Chart at the top ##
    # fig = gantt_chart()
    st.plotly_chart(fig)

    if st.session_state.cost_clicked:

        grid_response = AgGrid(
            dataframe = grid_cost_data,
            custom_css = custom_css,
            gridOptions = gridOptions, 
            height = grid_height,
            enable_enterprise_modules=True,
            fit_columns_on_grid_load=False,
            key = st.session_state.grid_key,   #- set a key to stop the grid reinitialising when the dataframe changes
            reload_data=True,  
            #   reload_data=False,  
            data_return_mode='AS_INPUT',
            #   data_return_mode='FILTERED',
            update_mode='VALUE_CHANGED',   ## default
            #   update_mode='MODEL_CHANGED',
            allow_unsafe_jscode=True,
            theme="light"  
                # 'streamlit'
                # "light" - balham-light
                # "dark" - balham-dark
                # "blue" - blue
                # "fresh" - fresh
                # "material" - material
        )

        # st.write(grid_response['data'].head(5))
        try:
            diff = grid_response['data'].compare(grid_cost_data)
        except:
            diff = 0
        # st.write(diff.head(5))
        if len(diff) > 0:
            changed_column = diff.columns[0][0]
            columns = diff.columns.tolist()
            # st.write("columns are =  ", columns)
            # if changed_column == 'forecast_method':
            #     st.session_state.grid_key = st.session_state.grid_key + 1
            new_value = diff.iloc[0,0]
            # st.write("new_value =  ", new_value)
            # st.write("index1 = ", diff.index.tolist()[0])
            # st.write("index2 = ", diff.index[0])
            cost_item_changed = grid_cost_data[(grid_cost_data.index==diff.index[0])].cost_item.iloc[0]
            # st.write("cost_item_changed =  ", cost_item_changed)
            st.write(f"new_value:  '{new_value}' in column: '{changed_column}' for item: '{cost_item_changed}'")
            
            if changed_column == 'item_end_date' or changed_column == 'item_start_date' or new_value == 'Timeline':
                df = st.session_state.reporting_month_forecast_data
                df.loc[df.cost_item == cost_item_changed, changed_column] = new_value
                st.session_state.reporting_month_forecast_data = df
                # st.button("press")
                st.experimental_rerun()
                # st.write(st.session_state.reporting_month_forecast_data)
            # new_series = diff['forecast_method', 'self'].dropna()
            # new_value_list = new_series.dropna().tolist()
            # new_column = new_series.name[0]
            # st.write("new_column: ", new_column)
            # new_value = new_series[0]
            # update_table(st.session_state.forecast_data_table_name, new_column, new_value, )
        # else:
        #     st.write("no changes detected")


    

if st.session_state.summary_clicked:
    grid_summary_data = pd.DataFrame(all_months)
    grid_summary_data['cost']=all_cost_amounts
    grid_summary_data['revenue']=st.session_state.revenue_amounts
    grid_summary_data['cashflow']= grid_summary_data['revenue'] - grid_summary_data['cost']
    cashflow_list = grid_summary_data['cashflow'].tolist()
    cum_sum=[]
    j=0
    for i in range(0,len(cashflow_list)):
        j+=cashflow_list[i]
        cum_sum.append(j)
    grid_summary_data['cum_cashflow'] = cum_sum
    # grid_summary_data
    gridOptions = configure_summary_grid_options()
    # gridOptions

    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        st.write("")
    with col2:
        grid_response = AgGrid(
            dataframe = grid_summary_data,
            gridOptions = gridOptions, 
            height = 500,
            enable_enterprise_modules=True,
            fit_columns_on_grid_load=False,
            key = 36,   #- set a key to stop the grid reinitialising when the dataframe changes
            reload_data=True,  
            #   reload_data=False,  
            data_return_mode='AS_INPUT',
            #   data_return_mode='FILTERED',
            update_mode='VALUE_CHANGED',   ## default
            #   update_mode='MODEL_CHANGED',
            allow_unsafe_jscode=True,
            theme="light" 
        )
    with col3:
        st.write("")


st.session_state.new_session = False
