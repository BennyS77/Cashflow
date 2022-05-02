import streamlit as st

st.sidebar.write('test')
st.sidebar.text_input('input')

#----------------------Hide Streamlit Hamburger Menu and footer----------------------------
hide_menu_footer = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_menu_footer, unsafe_allow_html=True)
#--------------------------------------------------------------------

markdown_container_style = """
<style>
.css-pbov4q {
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.6;
    text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: auto;
    color: rgb(33, 37, 41);
    box-sizing: border-box;
    font-family: "Source Sans Pro", sans-serif;
    background-color: rgb(150, 150, 255);
    margin-bottom: -1rem;
}
</style>
"""


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


#### Change all button colors
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}
div.stButton > button:hover {
    background-color: #00ff00;
    color:#ff0000;
    }
</style>""", unsafe_allow_html=True)