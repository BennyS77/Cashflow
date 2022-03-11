import pandas as pd
import streamlit as st


def getActualData():
    return pd.DataFrame.from_dict(
        {
            "costItem":['110','140','210'],
            "m0_amount":[250,175,140],
            "m1_amount":[150,125,160],
            "m2_amount":[180,90,25],
        }
    )

    
def initialiseData():
    grid_data= pd.DataFrame.from_dict(
        {
            "costGroup":['1','1','2'],
            "costItem":['110','140','210'],
            "EAC":[1000,3000,2000],
            "ACTD":[600,800,200],
        }
    )
    grid_data['startDate'] = st.session_state.start_date
    grid_data['endDate']   = st.session_state.end_date
    grid_data['numDaysRemaining']   =  (st.session_state.end_date - st.session_state.reporting_date).days
    grid_data['forecastMethod'] = "Timeline"
    return grid_data



def calculations(grid_data):
    #   grid_data = st.session_state.grid_data
    grid_data['ETC'] = grid_data['EAC'] - grid_data['ACTD']
    grid_data['accumPercent'] = grid_data['ACTD'] / grid_data['EAC']*100
    grid_data['percentPerDay'] = (grid_data['ETC'] / grid_data['EAC'])*100 / grid_data['numDaysRemaining']
    grid_data['daysLeft'] = grid_data['numDaysRemaining']
    for i in range(st.session_state.forecastMonths):
        grid_data['workDaysInMonth'] = grid_data.apply(lambda x: x['Month_'+str(i)+'_availDaysInMonth'] if x['daysLeft']>x['Month_'+str(i)+'_availDaysInMonth'] else x['daysLeft'], axis=1 )
        try:
            print(grid_data['Month_'+str(i)+'_accumPercent'])
        except:
            grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else 0, axis=1 )
        else:
            grid_data['Month_'+str(i)+'_accumPercent'] = grid_data.apply(lambda x: (x['workDaysInMonth']*x['percentPerDay'])+x['accumPercent'] if x['forecastMethod']=='Timeline' else x['Month_'+str(i)+'_accumPercent'], axis=1 )
        grid_data['Month_'+str(i)+'_amount'] = (grid_data['Month_'+str(i)+'_accumPercent'] - grid_data['accumPercent'])/100*grid_data['EAC']
        grid_data['daysLeft'] = grid_data['daysLeft'] - grid_data['workDaysInMonth']
        grid_data['accumPercent'] = grid_data['Month_'+str(i)+'_accumPercent']
    return grid_data