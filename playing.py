import streamlit as st
from cashflow_functions import fetch_Odata, get_odata_list, get_odata, user_login
st.write("start of script")

if 'login_confirmed' not in st.session_state:
    st.session_state.login_confirmed = False


st.write(st.session_state)


if not st.session_state.login_confirmed:
    user_login()


st.write("end of script")


# st.write(get_odata_list())

# st.write(get_odata())

# APPosted = fetch_Odata(
#             dataset = 'APPurchaseOrders',
#             columns='*',
#             filter=""
# )

st.button('sdf')
