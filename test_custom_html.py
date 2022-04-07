import streamlit as st

st.sidebar.write('test')
st.sidebar.text_input('input')

st.markdown("""
<style>
.css-fg4pbf {
    position: absolute;
    background: rgb(255, 255, 5);
    color: rgb(49, 51, 63);
    inset: 0px;
    overflow: hidden;
}
.css-zbg2rx {
    background-color: rgb(255, 0, 2);
    background-attachment: fixed;
    flex-shrink: 0;
    height: 100vh;
    overflow: auto;
    padding: 4rem 1rem;
    position: relative;
    transition: margin-left 1000ms ease 0s, box-shadow 1000ms ease 0s;
    width: 21rem;
    z-index: 100;
    margin-left: 0px;
}
.css-128j0gw {
    background-color: rgb(55, 245, 222);
    flex: 1 1 0%;
    width: 100%;
    padding: 0px;
    max-width: 46rem;
}
.st-br .st-ah {
    background-color: rgb(0, 255, 0);
    line-height: 4.6;
}
.row-widget {
    background-color: rgb(240, 220, 0);
    position: relative;
    width: 304px;
}
</style>
    """, unsafe_allow_html=True)
