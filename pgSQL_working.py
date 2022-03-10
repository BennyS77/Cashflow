from sqlalchemy import create_engine, text, delete
import streamlit as st


## create the 'engine' object using SQLite (which is in-mempry only)
# engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
engine = create_engine("postgresql+psycopg2://postgres:np22@127.0.0.1:5432/test_database", echo=True, future=True)

data_list = [{"x": 1, "y": 1}, {"x": 2, "y": 4}]


# with engine.connect() as conn:
#     conn.execute(text("DROP TABLE some_table"))
#     conn.commit()


with engine.connect() as conn:
    conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
         data_list
     )
    conn.commit()

with engine.connect() as conn:
    conn.execute(
         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
         [{"x": 9, "y": 9}]
     )
    conn.commit()

with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    #  st.write(result.all())
    for dict_row in result.mappings():
        st.write(dict_row)
        x = dict_row['x']
        y = dict_row['y']

st.write("filtering...")

with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {'y':2})
    for dict_row in result.mappings():
        st.write(dict_row)
        x = dict_row['x']
        y = dict_row['y']

st.write("Executing with an ORM Session...")
from sqlalchemy.orm import Session

st.write("updating table...")
with Session(engine) as session:
     result = session.execute(
         text("UPDATE some_table SET y=:y WHERE x=:x"),
         [{"x": 9, "y":11}, {"x": 2, "y": 15}]
     )
     session.commit()

stmt = text("SELECT x, y FROM some_table")
with Session(engine) as session:
    result = session.execute(stmt)
    for row in result:
         print(f"x: {row.x}  y: {row.y}")
         st.write(f"x: {row.x}  y: {row.y}")