from unicodedata import name
import streamlit as st

from my_config import page_config_and_session_state
from database_operations import table_names, drop_table

page_config_and_session_state()

"""
If you surround the table name with double quotes you can use hyphens!!!!!
"""


dodgyChar = '\u2013'


names = table_names().table_name.tolist()
names.append("")
st.write(names)

# st.write(dodgyChar)
# if '-' in names[4]:
#     st.write("DODGY")

# table_to_delete = st.text_input("table to delete:")
table_to_delete = st.selectbox(
                label = "Select a Table to delete:",
                options = names,
                index = (len(names)-1)
)
    
# my_table = '"report_data_rc50-1978"'
# st.write(my_table)

st.write(f"Table to delete: {table_to_delete}")

# drop_table(table_to_delete)

sql_query = 'DROP TABLE "' + table_to_delete + '"'
st.write(sql_query)
with st.session_state.engine.begin() as conn:
    conn.execute(sql_query)


st.write(f"DELETED table: '{table_to_delete}' from the database.")

names = table_names().table_name.tolist()
st.write(names)