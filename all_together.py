import streamlit as st
from my_config import page_config_and_session_state
from cashflow_functions import user_login, get_company, check_for_database_table

def get_company_list():
    st.session_state.company_list = ['AA','BB',""]

def get_job_list():
    st.session_state.job_list = ['A1101','B-202',""]

def company_change():
    st.session_state.job = ""
    st.session_state.job_list = []

def company_selectbox():
    st.sidebar.selectbox(label = "Choose Company:",
                    index = (len(st.session_state.company_list)-1), 
                    options = st.session_state.company_list,
                    key = "company",
                    on_change = company_change
                    )

def job_selectbox():
    if st.session_state.job_list == []:
        get_job_list()
    st.sidebar.selectbox(label = "Choose Job:",
                        # index = (len(st.session_state.job_list)-1), 
                        options = st.session_state.job_list,
                        key = 'job'
                        )

def report_month_selection():
    report_month_list = ["Dec 2021","Jan 2022","Feb 2022",""]
    st.sidebar.selectbox(label = "Choose Reporting Month:",
                        index = (len(report_month_list)-1), 
                        options = report_month_list,
                        )

def does_selected_month_data_exist():
    return False

def is_data_for_month_just_completed():
    return True




page_config_and_session_state()
ready_for_grid = False

if st.session_state.company_list == []:
    get_company_list()

company_selectbox()

if st.session_state.company != "":
    job_selectbox()

table_name = ("report_data_"+st.session_state.company+st.session_state.job).lower()

## """   IF A JOB HAS BEEN SELECTED  """
if st.session_state.job != "":
    # job_data_exists = check_for_database_table(table_name)
    job_data_exists = True
    if job_data_exists:
        st.sidebar.write(" Read job data from database.")
        st.sidebar.write(" Create a selection box to choose reporting month - existing and new months")
        report_month = report_month_selection()
        month_data_exists = does_selected_month_data_exist()
        if month_data_exists:
            st.sidebar.write(" The month chosen has existing data, so am using this.")
            data_is_latest = is_data_for_month_just_completed()
            if data_is_latest:
                refresh = st.sidebar.button("Refresh data:")
                if refresh:
                    st.sidebar.write("import Odata cost data")
                    st.sidebar.write(" Using refreshed data for the grid")
                    ready_for_grid = True
                else:
                    st.sidebar.write(" Using existing data for the grid")
                    ready_for_grid = True
            else:
                st.sidebar.write(" Use historical data for previous reporting months")
                st.sidebar.write(" Am now ready for the grid")
                ready_for_grid = True
        else:
            st.sidebar.write(" The month chosen does NOT have existing data (ie new), so am creating new report data with fresh cost data and existing forecast settings.")
            st.sidebar.write(" Data ready for grid.")
            ready_for_grid = True
    else:
        st.sidebar.write("Import Odata ")
        st.sidebar.write("Use latest completed calendar month to create new-job report data")
        st.sidebar.write(" Data ready for grid.")
        ready_for_grid = True


if ready_for_grid:
    st.sidebar.write("Generate grid.")


# st.write("Company: ", st.session_state.company)
# st.write("Job: ", st.session_state.job)

