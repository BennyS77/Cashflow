import streamlit as st
import os
from my_config import page_config_and_session_state


page_config_and_session_state()



root = os.path.join(os.path.dirname(__file__))

dashboards = {
    "Summary": os.path.join(root, "./views/summary.py"),
    "Cost": os.path.join(root, "./views/cost.py"),
    "Revenue": os.path.join(root, "./views/revenue.py"),
}

choice_from_url = query_params = st.experimental_get_query_params().get("notSureWhatThisIs", ["Cost"])[0]

index = list(dashboards.keys()).index(choice_from_url)

choice = st.sidebar.radio("View:", list(dashboards.keys()), index=index)


col1, col2 = st.sidebar.columns(2)
with col1:
    st.session_state.company_code = st.selectbox("Company code:",('ccTest','CoolComp','NearlyBroke'))
with col2:
    st.session_state.job_number = st.selectbox("Job number:",('BG700','TST121','WTF001'))


path = dashboards[choice]
with open(path, encoding="utf-8") as code:
    c = code.read()
    exec(c, globals())
