import streamlit as st

st.set_page_config(
      page_title="Premier Reports - Cost Forecast",
      page_icon="bar-chart",
      layout="wide",
      initial_sidebar_state="auto"  #expanded" #"collapsed" #auto
    )

hide_menu_footer = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""

header_style = """
<style>
/** Hide menu and footer **/
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

/** decorator **/
.css-fk4es0 {
    height: 0.2rem;
    background: rgba(255, 255, 255, 1);
}

/** header **/
.css-vw8ymm {
    font-size: 1rem;
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 400;
    line-height: 1.6;
    text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: auto;
    color: rgb(33, 37, 41);
    box-sizing: border-box;
    position: fixed;
    top: 0rem;
    left: 0px;
    right: 0px;
    height: 0rem;
    /*background: rgba(255, 255, 5, 1);*/
    /*backdrop-filter: blur(0px);*/
    z-index: 1000020;
    display: block;
}
/** Block container **/
.css-18e3th9 {
    font-size: 1rem;
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 400;
    line-height: 1.6;
    text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: auto;
    color: rgb(33, 37, 41);
    box-sizing: border-box;
    flex: 1 1 0%;
    width: 100%;
    padding: 0rem 1rem 5rem;
    min-width: auto;
    max-width: initial;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
    position: relative;
    /*background-color: rgb(15, 255, 255);*/

}
/** Button **/
.css-1on7ydh {
    text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: auto;
    box-sizing: border-box;
    font-size: inherit;
    font-family: inherit;
    overflow: visible;
    text-transform: none;
    appearance: button;
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 0rem 0rem;
    border-radius: 0.25rem;
    margin: 0rem;
    margin-left: 0rem;
    margin-top: 0.6rem;
    line-height: 1;
    color: rgba(1, 115, 198, 1);
    width: auto;
    user-select: none;
    background-color: rgba(1, 115, 198, 0);
    border: 1px solid rgba(33, 37, 41, 0);
    position: absolute;
    cursor: pointer;
    z-index: 200000000;
}
</style>
"""



button_style = """
<style>
.css-1on7ydh {
    text-size-adjust: 100%;
    -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    -webkit-font-smoothing: auto;
    box-sizing: border-box;
    font-size: inherit;
    font-family: inherit;
    overflow: visible;
    text-transform: none;
    appearance: button;
    display: inline-flex;
    -webkit-box-align: center;
    align-items: center;
    -webkit-box-pack: center;
    justify-content: center;
    font-weight: 400;
    padding: 0rem 0rem;
    border-radius: 0.25rem;
    margin: 0px;
    margin-top: 0rem;
    line-height: 1;
    color: inherit;
    width: auto;
    user-select: none;
    background-color: rgba(1, 115, 198, 0);
    border: 1px solid rgba(33, 37, 41, 0);
    cursor: pointer;
}
</style>
"""

st.markdown(header_style, unsafe_allow_html=True )
# st.markdown(button_style, unsafe_allow_html=True )







premier_blue_rgb = "rgba(1, 115, 198, 0.8)"
premier_blue_hex = "#0173C6"
white_rgb = "rgba(255,255,255,1)" 

premier_reports_html = """
    <h4
        style="
            text-align: left;
            margin-top:-2.5rem;
            margin-bottom:-1rem;
            padding-top:0.6rem;
            padding-bottom:0.6rem;
            padding-right:0rem;
            padding-left:2rem;
            font-weight:normal;
            background-image: linear-gradient(90deg, rgba(1, 115, 198, 1) 25%, rgba(255, 255, 255, 0.2) 100%, transparent);
            color:"""+white_rgb+""";
        "
        >PREMIER Reports
 </h4>
"""
            # background:"""+premier_blue_rgb+""";

client_id_html = """
    <h5
        style="
            text-align: right;
            margin-top:-0rem;
            margin-bottom:-1rem;
            padding-top:0.6rem;
            padding-bottom:0.2rem;
            padding-right:0rem;
            padding-left:0rem;
            font-weight:normal;
            font-size:95%;
            color:"""+premier_blue_rgb+""";
        "
        >Client ID: 810550
 </h5>
"""

divider_html = """
    <h5
        style="
            text-align: center;
            margin-top:0rem;
            margin-bottom:0rem;
            padding-top:0.6rem;
            padding-bottom:0.2rem;
            padding-right:6rem;
            padding-left:0rem;
            font-weight:normal;
            font-size:95%;
            color:"""+premier_blue_rgb+""";
        "
        >|
 </h5>
"""

start_month_html = """
    <p
        style="
            text-align: left;
            margin-top:-0.5rem;
            padding-top:0.6rem;
            padding-bottom:0.2rem;
            padding-right:2rem;
            padding-left:2rem;
            font-size:90%;
            font-weight:normal;
        "
        >Start month:
 </p>
"""
start_month_amount_html = """
    <h4
        style="
            text-align: center;
            margin-top:-1rem;
            padding-top:0.6rem;
            padding-bottom:0.2rem;
            padding-right:2rem;
            padding-left:2rem;
            font-weight:normal;
        "
        >Dec 2021:
 </h4>
"""


header_span_html = """
    <h3 style="
        margin-top: -4rem;
        padding-top:1rem;
        padding-bottom:1rem;
        padding-left:2rem;
        padding-right:0rem;
        text-align: left;
        background-image: linear-gradient(90deg, rgba(1, 115, 198, 1) 25%, rgba(255, 255, 255, 1) 100%);
        color:"""+white_rgb+""";">PREMIER Reports</h3>"""


col1, col2, col3, col4 = st.columns([20,4,0.2,2])
with col1:
    pass
with col2:
    st.markdown(client_id_html, unsafe_allow_html=True)
with col3:
    st.markdown(divider_html, unsafe_allow_html=True)
with col4:
    st.button("logout")

st.markdown(premier_reports_html, unsafe_allow_html=True )




# col1, col2, col3 = st.columns([56,1,3])
# with col1:
#     st.markdown(premier_reports_html, unsafe_allow_html=True )
#     st.markdown(client_id_html, unsafe_allow_html=True)
# with col2:
#     st.button("logout")
# with col3:
#     pass



col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([0.2,1,1.5,1, 1, 1, 1, 1, 0.2])
with col1:
    pass
with col2:
    company_ph = st.empty()
with col3:
    job_ph = st.empty()
with col4:
    reporting_month_ph = st.empty()
with col5:
    forecast_end_date_ph = st.empty()
with col6:
    start_month_ph1 = st.empty()
    start_month_ph2 = st.empty()
with col7:
    margin_ph1 = st.empty()
    margin_ph2 = st.empty()
with col8:
    pm_ph1 = st.empty()
    pm_ph2 = st.empty()
with col9:
    pass
#     # pm_ph = st.empty()

company_ph.selectbox(label = "Company:", options = ['NS Neverstop','NG Nevergo'])
job_ph.selectbox(label = "Job:", options = ['NSG21-010 Build something cool','NSG69-007 Have a rest day'])
reporting_month_ph.selectbox(label = "Reporting month:", options = ['DEC 2021','JAN 2022'])
forecast_end_date_ph.date_input(label = "Forecast End Date:")
start_month_ph1.markdown(start_month_html, unsafe_allow_html=True)
start_month_ph2.markdown(start_month_amount_html, unsafe_allow_html=True)

margin_ph1.markdown("##### Margin:")
margin_ph2.markdown("#### $355,670")
pm_ph1.markdown("##### Project Manager:")
pm_ph2.markdown("#### Thomas Edison")


    # font-size: 1rem;
    # font-weight: 400;
    # line-height: 1.6;
    # text-size-adjust: 100%;
    # -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
    # -webkit-font-smoothing: auto;
    # color: rgb(33, 37, 41);
    # box-sizing: border-box;
    # font-family: "Source Sans Pro", sans-serif;
    # margin-bottom: -1rem;

